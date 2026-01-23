#!/usr/bin/env python3
"""
Web interface for Nori health assistant.
"""

from flask import Flask, render_template, request, jsonify
from assistant import chat
from user_profile import display_profile, load_profile, save_profile
from memory import clear_history

app = Flask(__name__)
USER_ID = "web_user"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    data = request.json
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Handle commands
    if message.lower() == "/profile":
        profile = load_profile(USER_ID)
        profile_text = []
        if profile.get("name"):
            profile_text.append(f"Name: {profile['name']}")
        if profile.get("age"):
            profile_text.append(f"Age: {profile['age']}")
        if profile.get("location"):
            profile_text.append(f"Location: {profile['location']}")
        if profile.get("conditions"):
            profile_text.append(f"Conditions: {', '.join(profile['conditions'])}")
        if profile.get("medications"):
            profile_text.append(f"Medications: {', '.join(profile['medications'])}")
        if profile.get("allergies"):
            profile_text.append(f"Allergies: {', '.join(profile['allergies'])}")
        if not profile_text:
            profile_text = ["No profile information yet."]
        return jsonify({"messages": profile_text})

    if message.lower() in ["/new", "/clear"]:
        clear_history(USER_ID)
        return jsonify({"messages": ["New conversation started. Profile retained."]})

    if message.lower() == "/reset":
        clear_history(USER_ID)
        save_profile(USER_ID, {
            "name": None,
            "age": None,
            "location": "USA",
            "conditions": [],
            "medications": [],
            "allergies": [],
            "health_goals": [],
            "notes": []
        })
        return jsonify({"messages": ["Profile and history reset."]})

    # Get response from assistant
    response = chat(USER_ID, message)

    # Split response into paragraphs for multiple bubbles
    paragraphs = [p.strip() for p in response.split("\n\n") if p.strip()]

    return jsonify({"messages": paragraphs})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
