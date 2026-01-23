import json
from pathlib import Path
from memory import get_user_dir


DEFAULT_PROFILE = {
    "name": None,
    "age": None,
    "location": "USA",     # default, updated if user mentions location
    "conditions": [],      # e.g., ["high blood pressure", "type 2 diabetes"]
    "medications": [],     # e.g., ["lisinopril 10mg daily", "metformin"]
    "allergies": [],       # e.g., ["penicillin", "shellfish"]
    "health_goals": [],    # e.g., ["lose weight", "run a 5k"]
    "notes": []            # misc facts, e.g., ["prefers natural remedies", "works night shifts"]
}


def load_profile(user_id: str) -> dict:
    """Load user profile, creating default if doesn't exist."""
    profile_file = get_user_dir(user_id) / "profile.json"
    if profile_file.exists():
        return json.loads(profile_file.read_text())
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
    if profile.get("age"):
        lines.append(f"Age: {profile['age']}")
    if profile.get("location"):
        lines.append(f"Location: {profile['location']}")
    if profile.get("conditions"):
        lines.append(f"Conditions: {', '.join(profile['conditions'])}")
    if profile.get("medications"):
        lines.append(f"Medications: {', '.join(profile['medications'])}")
    if profile.get("allergies"):
        lines.append(f"Allergies: {', '.join(profile['allergies'])}")
    if profile.get("health_goals"):
        lines.append(f"Health goals: {', '.join(profile['health_goals'])}")
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
    output.append(f"Age: {profile.get('age') or 'Not set'}")
    output.append(f"Location: {profile.get('location') or 'USA'}")
    output.append(f"Conditions: {', '.join(profile['conditions']) or 'None recorded'}")
    output.append(f"Medications: {', '.join(profile['medications']) or 'None recorded'}")
    output.append(f"Allergies: {', '.join(profile['allergies']) or 'None recorded'}")
    output.append(f"Health goals: {', '.join(profile['health_goals']) or 'None set'}")
    output.append(f"Notes: {', '.join(profile['notes']) or 'None'}")
    output.append("====================\n")

    return "\n".join(output)
