# KeyCrypt

KeyCrypt is a fun and challenging puzzle and messaging site. You can create puzzles for friends and other players to solve! Only then can they decrypt your message.

Access it on [keycrypt.mlziade.com.br](https://keycrypt.mlziade.com.br)!

## Features

*   **Puzzle Creation**: Design personalized puzzles with custom questions where answers serve as cryptographic keys.
*   **Easy Sharing**: Share puzzles via unique IDs and direct URLs.
*   **Hint System**: Get hints to guide you to the answer.
*   **Testing Answers**: Test if answers are "correct", "close" or "wrong".
*   **Access Controls**: Set puzzles as view-only or configure auto-deletion after specified time periods.
*   **Daily Challenges**: Tackle thematic puzzles created by our team of models ;)
*   **Weekly leaderboards**: To encourage friendly competition.
*   **User Profiles**: Track created and solved puzzles in your personalized profile page.

## Roadmap

*   Performance optimization via caching for high-traffic puzzles.
*   Security enhancements including rate-limiting to prevent brute-force attempts.
*   Direct messaging system between users.

## Infrastructure

*   Deployed on an Ubuntu Linux server on a Hetzner VPS.
*   Django backend with sqlite database
*   Uses Gunicorn as the WSGI production server.
*   Nginx as the reverse proxy for handling incoming calls.
*   Ollama as the LLM model provided on the machine.

test ci/cd