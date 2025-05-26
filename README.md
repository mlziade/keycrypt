# KeyCrypt

KeyCrypt is a fun and challenging puzzle and messaging site. You can create puzzles for friends and other players to solve! Only then can they decrypt your message.

~~Access it on [keycrypt.mlziade.com.br](https://keycrypt.mlziade.com.br)!~~

**Note:** The website has been deactivated and is no longer available.

## Features

*   **Puzzle Creation**: Design personalized puzzles with custom questions where answers serve as cryptographic keys.
*   **Easy Sharing**: Share puzzles via unique IDs and direct URLs.
*   **Hint System**: Get hints to guide you to the answer.
*   **Testing Answers**: Test if answers are "correct", "close" or "wrong".
*   **Access Controls**: Set puzzles as view-only or configure auto-deletion after specified time periods.
*   **Daily Challenges**: Tackle thematic puzzles created by our team of models ;)
*   **Weekly leaderboards**: To encourage friendly competition.
*   **User Profiles**: Track created and solved puzzles in your personalized profile page.

## Pictures

<p align="center">
  <img src="docs/example1.png" alt="Puzzle creation page" width="500"><br>
  <em>Puzzle creation page: Create custom puzzles with your own questions and answers.</em>
</p>

<p align="center">
  <img src="docs/example.png" alt="Solving a puzzle" width="500"><br>
  <em>Solving a puzzle: Enter answers to unlock the encrypted message.</em>
</p>

<p align="center">
  <img src="docs/example3.png" alt="Daily challenge leaderboard" width="500"><br>
  <em>Daily challenge leaderboard: Compete with others and track your progress.</em>
</p>

<p align="center">
  <img src="docs/example2.png" alt="User profile page" width="500"><br>
  <em>User profile page: View your created and solved puzzles.</em>
</p>

## Roadmap

*   Performance optimization via caching for high-traffic puzzles.
*   ✅ Security enhancements including rate-limiting to prevent brute-force attempts.
*   Direct messaging system between users.

## Infrastructure

*   Deployed on an Ubuntu Linux server on a Hetzner VPS.
*   Django backend with sqlite database
*   Uses Gunicorn as the WSGI production server.
*   Nginx as the reverse proxy for handling incoming calls.
*   Ollama as the LLM model provided on the machine.