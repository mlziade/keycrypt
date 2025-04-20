import os
import re
import json
import random
import requests
from datetime import datetime, date
from django.core.management.base import BaseCommand

from daily.models import DailyChallenge
from puzzle.models import PuzzleQuestion, PuzzleQuestionHint

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
    "Studio Ghibli",
    "Naruto",
    "One Piece",
    "Pop Music Hits",
    "Rock Legends",
    "Hip Hop & Rap",
    "World Capitals",
    "Famous Landmarks",
    "Street Food Around the World",
    "Fast Food Chains",
    "Mythology & Legends",
    "Video Games",
    "Retro Cartoons",
    "Oscars & Awards",
    "Fantasy Worlds",
]


difficulty_levels: list[str] = [
    "Easy",
    "Medium",
    "Hard"
]

def extract_json_from_markdown(text) -> str | None:
    """
    Extract JSON data from markdown code blocks in the LLM response.
    ```json
    { json content }
    ```
    """
    pattern = r'```json\s*(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0] if matches else None

def read_prompt_from_file() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'daily_challenge_prompt.txt')
    
    with open(file_path, 'r') as file:
        return file.read()

def call_ollama_server(prompt, model):
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Response from server: {response.json()}")
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

class Command(BaseCommand):
    help = "Generate a daily challenge for the current day"

    def handle(self, *args, **kwargs):
        # Get the current date
        today = date.today()

        theme = trivia_themes[random.randint(0, len(trivia_themes) - 1)]
        difficulty = difficulty_levels[random.randint(0, len(difficulty_levels) - 1)]

        prompt: str = read_prompt_from_file()
        prompt = prompt.replace("<<REPLACE_THEME>>", theme)
        prompt = prompt.replace("<<REPLACE_DIFFICULTY>>", difficulty)    

        self.stdout.write(f"Generating challenge for {today} with theme '{theme}'...")

        challenge_data = call_ollama_server(
            prompt=prompt,
            model="gemma3:1b"
        )

        if not challenge_data:
            self.stdout.write(self.style.ERROR("Failed to get response from Ollama server"))
            return

        # Extract JSON from the response field (which contains markdown)
        json_str = extract_json_from_markdown(challenge_data.get('response', ''))
        
        if not json_str:
            self.stdout.write(self.style.ERROR("Could not extract JSON from the response"))
            return

        try:
            # Parse the JSON data
            data = json.loads(json_str)
            self.stdout.write(f"Challenge for {today} parsed successfully")
            
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
                question = PuzzleQuestion(
                    puzzle=daily_challenge,
                    question=q_data['question'],
                    solution=q_data['answer']
                )
                question.save()
                solutions.append(q_data['answer'])
                
                # Create hint if available
                if 'hint' in q_data:
                    hint = PuzzleQuestionHint(
                        question=question,
                        hint=q_data['hint']
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
            
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Invalid JSON format in the response"))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f"Missing required key in JSON: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating daily challenge: {e}"))