#!/usr/bin/env python3
"""
Nori - AI Health Assistant with Memory

A health assistant that remembers your conversations and builds
a profile of your health over time.
"""

import sys
from assistant import chat_stream
from user_profile import display_profile, load_profile, save_profile
from memory import clear_history

# Default user ID (in a real app, this would come from auth)
USER_ID = "default"


def print_help():
    print("""
Commands:
  /profile  - View your health profile
  /new      - Start new conversation (keeps profile)
  /clear    - Same as /new
  /reset    - Reset everything (profile + history)
  /help     - Show this help
  /quit     - Exit
""")


def handle_command(command: str) -> bool:
    """Handle slash commands. Returns True if should continue, False to quit."""
    cmd = command.lower().strip()

    if cmd == "/quit" or cmd == "/exit":
        print("Take care!")
        return False

    elif cmd == "/help":
        print_help()

    elif cmd == "/profile":
        print(display_profile(USER_ID))

    elif cmd == "/clear" or cmd == "/new":
        clear_history(USER_ID)
        print("New conversation started. (Profile retained)")

    elif cmd == "/reset":
        clear_history(USER_ID)
        save_profile(USER_ID, {
            "name": None,
            "age": None,
            "conditions": [],
            "medications": [],
            "allergies": [],
            "health_goals": [],
            "notes": []
        })
        print("Profile and history reset.")

    else:
        print(f"Unknown command: {command}")
        print_help()

    return True


def main():
    print("Nori - Health Assistant")
    print("Type /help for commands, /quit to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.startswith("/"):
                if not handle_command(user_input):
                    break
                continue

            # Stream the response
            print("Bot: ", end="", flush=True)
            for chunk in chat_stream(USER_ID, user_input):
                print(chunk, end="", flush=True)
            print("\n")

        except KeyboardInterrupt:
            print("\nTake care!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
