import os
import re
import json
import random
import requests
from datetime import datetime, date
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from daily.models import DailyChallenge
from puzzle.models import PuzzleQuestion, PuzzleQuestionHint
from puzzle.forms import CreatePuzzleForm
from daily.forms import CreateDailyPuzzleForm

load_dotenv()

trivia_themes: list[str] = [
    "Marvel Cinematic Universe",
    "Harry Potter",
    "Star Wars",
    "Friends (TV Series)",
    "Stranger Things",
    "The Office",
    "Game of Thrones",
    "Disney",
    "Pixar",
    "Naruto",
    "One Piece",
    "Pop Music of the 2000s",
    "World Capitals",
    "Famous Landmarks",
    "Fast Food Chains",
    "Greek and Roman Mythology",
    "Famous Video Games",
    "Oscars & Awards",
    "Lord of the Rings and Hobbit",
]

difficulty_levels: list[str] = [
    "easy",
    "medium",
    "hard"
]

def extract_json_from_markdown(text) -> dict:
    """
    Extract JSON data from markdown code blocks in the LLM response.
    ```json
    { json content }
    ```
    """
    pattern = r'```json\s*(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if not matches:
        raise ValueError("No JSON code block found in the response")
    
    try:
        return json.loads(matches[0])
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON format: {e}", matches[0], e.pos)

def read_prompt_from_file() -> str:
    """
    Read the daily challenge prompt from a file.
    The file should be located in the same directory as this script.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'daily_challenge_prompt.txt')
    
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt template not found at: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading prompt template: {e}")

def call_ollama_server(prompt, model):
    """
    Call the Ollama server to generate a daily challenge.
    """

    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=300) # 5 minutes timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("Error: The request to the Ollama server timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to the Ollama server: {e}")
        return None

def validate_hint(hint: str) -> bool:
    """
    Validate that a hint is at most 2 words and 30 characters.
    """
    if not hint:
        return True
    
    if len(hint) > 30:
        return False
    
    if len(hint.split()) > 2:
        return False
    
    return True

class Command(BaseCommand):
    help = "Create a daily challenge using LLM for the current day"

    def handle(self, *args, **kwargs):
        # Get the current date
        today = date.today()

        # Check if a challenge already exists for today
        if DailyChallenge.objects.filter(daily_date=today).exists():
            self.stdout.write(self.style.WARNING(f"Daily challenge for {today} already exists."))
            return

        # Select a random theme and difficulty level
        theme = random.choice(trivia_themes)
        difficulty = random.choice(difficulty_levels)

        prompt: str = read_prompt_from_file()
        prompt = prompt.replace("<<REPLACE_THEME>>", theme)
        prompt = prompt.replace("<<REPLACE_DIFFICULTY>>", difficulty)    

        self.stdout.write(f"Generating challenge for {today} with theme '{theme}'...")

        challenge_data = call_ollama_server(
            prompt=prompt,
            model=os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
        )

        if not challenge_data:
            self.stdout.write(self.style.ERROR("Failed to get response from Ollama server"))
            return

        try:
            # Extract JSON from the response field (which contains markdown)
            data = extract_json_from_markdown(challenge_data.get('response', ''))
            self.stdout.write(f"Challenge for {today} parsed successfully")
            
            # Validate message length (max 280 characters)
            if 'message' not in data or len(data['message']) > 280:
                self.stdout.write(self.style.ERROR("Message is missing or exceeds 280 character limit"))
                return
            
            # Validate difficulty is one of the allowed choices
            if data['difficulty'] not in [choice.lower() for choice in DailyChallenge.DifficultyChoices.values]:
                self.stdout.write(self.style.ERROR(f"Invalid difficulty: {data['difficulty']}"))
                return
            
            # Create a new DailyChallenge
            daily_challenge = DailyChallenge(
                theme=data['theme'],
                difficulty=data['difficulty'].lower(),
                daily_date=today,
                one_time_view=False,
                is_solved=False,
                self_destruct_at=None,
                created_by=None,
                encrypted_message='',
                nonce='',
                salt=''
            )
            daily_challenge.save()
            
            # Store solutions for encryption
            solutions = []
            
            # Create questions and hints
            for q_data in data['questions']:
                # Validate solution length (max 50 characters)
                if 'answer' not in q_data or len(q_data['answer']) > 50:
                    self.stdout.write(self.style.ERROR(f"Solution missing or exceeds 50 character limit: {q_data.get('answer', '')}"))
                    daily_challenge.delete()  # Clean up partial challenge
                    return
                
                question = PuzzleQuestion(
                    puzzle=daily_challenge,
                    question=q_data['question'],
                    solution=q_data['answer']
                )
                question.save()
                solutions.append(q_data['answer'])
                
                # Create hint if available, after validating
                if 'hint' in q_data:
                    hint_text = q_data['hint']
                    # Validate hint (max 2 words, 30 characters)
                    if not validate_hint(hint_text):
                        self.stdout.write(self.style.WARNING(f"Skipping invalid hint: {hint_text}"))
                        continue
                        
                    hint = PuzzleQuestionHint(
                        question=question,
                        hint=hint_text
                    )
                    hint.save()
            
            # Encrypt the message
            from puzzle.services import encrypt_message
            solutions.sort()
            encrypted_message = encrypt_message(
                words=solutions,
                message=data['message']
            )
            
            # Save the encrypted message details
            daily_challenge.encrypted_message = encrypted_message['ciphertext']
            daily_challenge.nonce = encrypted_message['nonce']
            daily_challenge.salt = encrypted_message['salt']
            daily_challenge.save()
            
            self.stdout.write(self.style.SUCCESS(
                f"Daily challenge for {today} created successfully with theme '{data['theme']}'"
            ))
            
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Error extracting JSON: {e}"))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Invalid JSON format in the response"))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"Missing required key in JSON: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating daily challenge: {e}"))
