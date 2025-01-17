# CheriPit Bot

A discord bot for the CheriPit Discord server

## Features

1. Whenver a variation of one of these terms are mentioned, responds with a random gif associated with it: 
- liar's bar
- fortnite
- lethal company
- among us
- minecraft
- zelda
- brawl stars
- hamster
- joe biden
- donald trump
- peter griffin
- costco
- voice chat

2. Responds with a comment when a score from one of these games is shared:
- Wordle
- Connections

## Getting Started

### Prerequisites

1. [Python](https://www.python.org/downloads/)
2. [Git](https://git-scm.com/downloads)

### Discord Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.

2. TODO

### Bot Setup

1. Clone the repository and install dependencies
```bash
git clone https://github.com/gusev03/brain-rot-bot.git
cd brain-rot-bot
```

2. Create a virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate # on Windows use ".venv\Scripts\activate"
pip install -r requirements.txt
```

3. Create a `.env` file with your discord bot token:
```bash
echo "DISCORD_TOKEN=<your_token>" > .env # Remove quotes for Windows; replace <your_token> with your discord bot token
```

4. Run the bot
```bash
python bot.py
```
