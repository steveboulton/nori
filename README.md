# Nori

AI health assistant with memory. Like a doctor in the family—professional expertise with genuine warmth.

## Features

- **Conversational memory** - Remembers your health history across sessions
- **User profile** - Tracks conditions, medications, allergies, goals
- **Action-oriented** - Gives you links to tests, supplements, and resources
- **SMS-style** - Short, direct responses
- **Web interface** - Chat UI that looks like iMessage

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
```

## Usage

### CLI
```bash
python main.py
```

### Web
```bash
python web.py
```
Then open http://localhost:5001

## Commands

- `/profile` - View your health profile
- `/new` - Start new conversation (keeps profile)
- `/reset` - Reset everything

## Architecture

```
nori/
├── main.py           # CLI entry point
├── web.py            # Flask web server
├── assistant.py      # Claude integration
├── memory.py         # Conversation storage
├── user_profile.py   # Profile management
├── config.py         # Settings
├── prompts/
│   ├── system.txt    # System prompt
│   └── resources.txt # URL patterns
└── templates/
    └── index.html    # Web chat UI
```
