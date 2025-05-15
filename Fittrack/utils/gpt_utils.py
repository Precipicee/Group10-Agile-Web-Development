import openai
import os
print("✔️ ENV loaded? OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))

import re
from flask import current_app

def estimate_calories_from_meal(meal_description: str) -> float:
    openai.api_key = current_app.config['OPENAI_API_KEY'] 

    prompt = f"""
    You are a calorie estimation assistant. Estimate the total calorie count for the following daily meals. 
    The description may contain quantities, approximations, or embedded calorie hints. 
    Use common nutritional knowledge and reasoning.
    Return ONLY a single number like 1850 — no text, no units, no JSON.
    Meals:
    {meal_description}
    """


    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        result = response['choices'][0]['message']['content']
        print("[DEBUG] GPT Raw Result:", result)


        match = re.search(r"\d+(\.\d+)?", result)
        if match:
            return float(match.group(0))
        else:
            print("[WARN] No number found in GPT response.")
            return -1.0

    except Exception as e:
        print(f"[ERROR] GPT API Failed:", e)
        return -1.0


def estimate_calories_from_exercise(exercise_list: list) -> float:
    """
    exercise_list: list of dicts like:
    [{"type": "Running", "duration": "30", "intensity": "high"}, ...]
    """

    openai.api_key = current_app.config['OPENAI_API_KEY']

    # Convert to readable text
    exercise_description = "\n".join(
        f"- {e['type']}: {e['duration']} minutes, {e['intensity']} intensity"
        for e in exercise_list
    )

    prompt = f"""
You are a fitness assistant. Estimate the total calories burned based on the following exercises.
Return only a number like 450 — no units, no text, no explanation.
{exercise_description}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        result = response['choices'][0]['message']['content']
        print("[DEBUG] GPT EXERCISE Result:", result)

        match = re.search(r"\d+(\.\d+)?", result)
        if match:
            return float(match.group(0))
        else:
            print("[WARN] No number found in GPT response.")
            return -1.0

    except Exception as e:
        print(f"[ERROR] GPT API Failed:", e)
        return -1.0
