from typing import Optional
import json
from datetime import datetime
import anthropic
from config import ANTHROPIC_API_KEY, MODEL, PROMPTS_DIR
from memory import get_recent_history, save_conversation_turn
from user_profile import format_profile_for_prompt, load_profile, save_profile

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def load_system_prompt() -> str:
    """Load the system prompt template from file."""
    prompt_file = PROMPTS_DIR / "system.txt"
    return prompt_file.read_text()


def load_resources() -> str:
    """Load URL patterns for services."""
    resources_file = PROMPTS_DIR / "resources.txt"
    if resources_file.exists():
        return resources_file.read_text()
    return ""


def build_system_prompt(user_id: str) -> str:
    """Build the complete system prompt with user profile and resources."""
    template = load_system_prompt()
    profile_text = format_profile_for_prompt(user_id)
    resources = load_resources()

    current_date = datetime.now().strftime("%B %d, %Y")
    prompt = template.format(user_profile=profile_text, current_date=current_date)
    if resources:
        prompt += f"\n\n{resources}"
    return prompt


def extract_profile_updates(user_id: str, user_message: str, assistant_response: str) -> Optional[dict]:
    """Use Claude to extract any new profile information from the conversation."""
    profile = load_profile(user_id)

    extraction_prompt = f"""Analyze this conversation exchange and extract any NEW information about the user that should be remembered for their weight loss plan.

Current known profile:
{format_profile_for_prompt(user_id)}

User said: {user_message}
Assistant responded: {assistant_response}

If there's new information to add, respond with a JSON object containing only the fields to update:
- name: string
- height: string (e.g., "5'10\"" or "178 cm")
- current_weight: string (e.g., "210 lbs" or "95 kg")
- target_weight: string (e.g., "180 lbs" or "82 kg")
- target_date: string (e.g., "June 2025", "6 months from now")
- conditions: list of medical conditions to ADD
- current_diet: string (summary of typical daily eating)
- current_exercise: string (summary of current activity level)
- diet_preferences: list of preferences to ADD (e.g., "vegetarian", "hates broccoli")
- exercise_preferences: list of preferences to ADD (e.g., "likes walking", "no gym access")
- chosen_strategies: list of strategies to ADD (e.g., "diet", "exercise", "GLP-1")
- barriers: list of barriers to ADD (e.g., "travels for work", "stress eating")
- plan: string (the weight loss plan if one was generated)
- committed: boolean (true if user explicitly committed to the plan)
- notes: list of relevant facts to ADD

Only include fields where you found NEW information not already in the profile.
If nothing new was learned, respond with exactly: null

Respond with ONLY the JSON object or null, no other text."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    response_text = response.content[0].text.strip()

    if response_text == "null" or not response_text:
        return None

    try:
        updates = json.loads(response_text)
        if updates:
            # Merge updates into profile
            for key, value in updates.items():
                if key in profile:
                    if isinstance(profile[key], list) and isinstance(value, list):
                        for item in value:
                            if item not in profile[key]:
                                profile[key].append(item)
                    elif isinstance(profile[key], list):
                        if value not in profile[key]:
                            profile[key].append(value)
                    else:
                        profile[key] = value

            save_profile(user_id, profile)
            return updates
    except json.JSONDecodeError:
        pass

    return None


GREETING = "Hi — I'm your weight loss coach. I'll ask a few questions to build a plan tailored to you.\n\nHow much weight are you looking to lose?"


def chat(user_id: str, user_message: str) -> str:
    """Send a message and get a response, managing memory automatically."""
    # Save user message
    save_conversation_turn(user_id, "user", user_message)

    # Build context
    system_prompt = build_system_prompt(user_id)
    history = get_recent_history(user_id)

    # Seed the conversation with the greeting so the model sees itself on-track
    if len(history) == 1:
        # First user message — inject the greeting as prior assistant turn
        history = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": GREETING},
        ] + history

    # Get response from Claude
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=history
    )

    assistant_message = response.content[0].text

    # Save assistant response
    save_conversation_turn(user_id, "assistant", assistant_message)

    # Extract and save any new profile information
    extract_profile_updates(user_id, user_message, assistant_message)

    return assistant_message


def chat_stream(user_id: str, user_message: str):
    """Stream a response, yielding chunks as they arrive."""
    # Save user message
    save_conversation_turn(user_id, "user", user_message)

    # Build context
    system_prompt = build_system_prompt(user_id)
    history = get_recent_history(user_id)

    # Seed the conversation with the greeting so the model sees itself on-track
    if len(history) == 1:
        history = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": GREETING},
        ] + history

    # Stream response from Claude
    full_response = ""
    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=history
    ) as stream:
        for text in stream.text_stream:
            full_response += text
            yield text

    # Save assistant response
    save_conversation_turn(user_id, "assistant", full_response)

    # Extract profile updates after streaming completes
    extract_profile_updates(user_id, user_message, full_response)
