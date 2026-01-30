import json
from pathlib import Path
from memory import get_user_dir


DEFAULT_PROFILE = {
    "name": None,
    "height": None,          # e.g., "5'10\"" or "178 cm"
    "current_weight": None,  # e.g., "210 lbs" or "95 kg"
    "target_weight": None,   # e.g., "180 lbs" or "82 kg"
    "target_date": None,     # e.g., "June 2025", "6 months"
    "conditions": [],        # e.g., ["type 2 diabetes", "bad knees"]
    "current_diet": None,    # free text summary of typical eating
    "current_exercise": None,  # free text summary of current activity
    "diet_preferences": [],  # e.g., ["vegetarian", "hates fish", "can't cook much"]
    "exercise_preferences": [],  # e.g., ["likes walking", "has gym membership"]
    "chosen_strategies": [], # e.g., ["diet", "exercise"]
    "barriers": [],          # e.g., ["travels for work", "stress eating"]
    "plan": None,            # the generated plan text
    "committed": None,       # True/False — did they commit?
    "notes": []              # misc facts
}


def load_profile(user_id: str) -> dict:
    """Load user profile, creating default if doesn't exist."""
    profile_file = get_user_dir(user_id) / "profile.json"
    if profile_file.exists():
        saved = json.loads(profile_file.read_text())
        # Merge with defaults to pick up any new fields
        merged = DEFAULT_PROFILE.copy()
        merged.update(saved)
        return merged
    return DEFAULT_PROFILE.copy()


def save_profile(user_id: str, profile: dict):
    """Save user profile."""
    profile_file = get_user_dir(user_id) / "profile.json"
    profile_file.write_text(json.dumps(profile, indent=2))


def update_profile(user_id: str, **updates):
    """Update specific fields in user profile."""
    profile = load_profile(user_id)

    for key, value in updates.items():
        if key in profile:
            if isinstance(profile[key], list) and not isinstance(value, list):
                # Append to list fields
                if value not in profile[key]:
                    profile[key].append(value)
            else:
                profile[key] = value

    save_profile(user_id, profile)
    return profile


def format_profile_for_prompt(user_id: str) -> str:
    """Format user profile as text for the system prompt."""
    profile = load_profile(user_id)

    lines = []

    if profile.get("name"):
        lines.append(f"Name: {profile['name']}")
    if profile.get("height"):
        lines.append(f"Height: {profile['height']}")
    if profile.get("current_weight"):
        lines.append(f"Current weight: {profile['current_weight']}")
    if profile.get("target_weight"):
        lines.append(f"Target weight: {profile['target_weight']}")
    if profile.get("target_date"):
        lines.append(f"Target date: {profile['target_date']}")
    if profile.get("conditions"):
        lines.append(f"Medical conditions: {', '.join(profile['conditions'])}")
    if profile.get("current_diet"):
        lines.append(f"Current diet: {profile['current_diet']}")
    if profile.get("current_exercise"):
        lines.append(f"Current exercise: {profile['current_exercise']}")
    if profile.get("diet_preferences"):
        lines.append(f"Diet preferences: {', '.join(profile['diet_preferences'])}")
    if profile.get("exercise_preferences"):
        lines.append(f"Exercise preferences: {', '.join(profile['exercise_preferences'])}")
    if profile.get("chosen_strategies"):
        lines.append(f"Chosen strategies: {', '.join(profile['chosen_strategies'])}")
    if profile.get("barriers"):
        lines.append(f"Barriers: {', '.join(profile['barriers'])}")
    if profile.get("plan"):
        lines.append(f"Current plan: {profile['plan']}")
    if profile.get("committed") is not None:
        lines.append(f"Committed to plan: {'Yes' if profile['committed'] else 'No'}")
    if profile.get("notes"):
        lines.append(f"Other notes: {', '.join(profile['notes'])}")

    if not lines:
        return "No information known yet about this person."

    return "\n".join(lines)


def display_profile(user_id: str) -> str:
    """Get a human-readable display of the profile."""
    profile = load_profile(user_id)

    output = ["\n=== Your Profile ==="]
    output.append(f"Name: {profile.get('name') or 'Not set'}")
    output.append(f"Height: {profile.get('height') or 'Not set'}")
    output.append(f"Current weight: {profile.get('current_weight') or 'Not set'}")
    output.append(f"Target weight: {profile.get('target_weight') or 'Not set'}")
    output.append(f"Target date: {profile.get('target_date') or 'Not set'}")
    output.append(f"Conditions: {', '.join(profile.get('conditions', [])) or 'None recorded'}")
    output.append(f"Current diet: {profile.get('current_diet') or 'Not captured'}")
    output.append(f"Current exercise: {profile.get('current_exercise') or 'Not captured'}")
    output.append(f"Strategies: {', '.join(profile.get('chosen_strategies', [])) or 'Not chosen'}")
    output.append(f"Barriers: {', '.join(profile.get('barriers', [])) or 'None noted'}")
    output.append(f"Committed: {profile.get('committed') or 'Pending'}")
    output.append(f"Notes: {', '.join(profile.get('notes', [])) or 'None'}")
    output.append("====================\n")

    return "\n".join(output)
