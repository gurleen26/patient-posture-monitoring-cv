from src.llm_feedback import get_ai_feedback

# Fake some angle data
angles = {
    "left_knee": 177.5,
    "right_knee": 97.5,
    "spine": 175.6,
    "left_shoulder": 177.1,
    "right_shoulder": 175.6
}

analysis = {
    "status": "Needs correction",
    "issues": ["Right knee bent too much", "Knee asymmetry: 80.0 deg difference"]
}

feedback = get_ai_feedback(angles, "warrior", analysis)
print(feedback)