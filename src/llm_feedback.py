from groq import Groq

def get_ai_feedback(angles: dict, exercise: str, analysis: dict) -> str:
    client = Groq()  # reads GROQ_API_KEY from env

    issues = analysis.get("issues", [])
    issues_text = "\n".join(f"- {i}" for i in issues) if issues else "- None flagged"

    prompt = f"""You are a physiotherapy assistant. A patient is doing a {exercise} exercise.

Joint angles measured:
- Left knee: {angles.get('left_knee', 'N/A')}°
- Right knee: {angles.get('right_knee', 'N/A')}°
- Spine: {angles.get('spine', 'N/A')}°
- Left shoulder: {angles.get('left_shoulder', 'N/A')}°
- Right shoulder: {angles.get('right_shoulder', 'N/A')}°

Issues flagged: {issues_text}

Give a 2-3 sentence clinical assessment. Be specific and encouraging."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content