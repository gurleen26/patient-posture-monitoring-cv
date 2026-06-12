import cv2

GREEN  = (0, 200, 0)
RED    = (0, 0, 220)
WHITE  = (255, 255, 255)
YELLOW = (0, 255, 255)
FONT   = cv2.FONT_HERSHEY_SIMPLEX

# Only show these angles on screen — skip asymmetry raw values
DISPLAY_ANGLES = {
    "left_knee":   "L Knee",
    "right_knee":  "R Knee",
    "spine":       "Spine",
    "shoulder":    "L Shoulder",
    "right_shoulder": "R Shoulder",
}

def draw_angles(frame, angles):
    h, w = frame.shape[:2]

    # Fix — use fixed font scale instead of dynamic scaling
    font_scale = 0.7
    thickness  = 2

    y        = 40
    line_gap = 35

    for key, label in DISPLAY_ANGLES.items():
        val = angles.get(key)
        if val is None:
            continue
        text = f"{label}: {val}"

        # Add black outline for readability on any background
        cv2.putText(frame, text, (20, y), FONT, font_scale,
                    (0, 0, 0), thickness + 2)        # black outline
        cv2.putText(frame, text, (20, y), FONT, font_scale,
                    WHITE, thickness)                  # white text on top
        y += line_gap

    # Asymmetry in yellow with outline
    knee_asym     = angles.get("knee_asymmetry")
    shoulder_asym = angles.get("shoulder_asymmetry")

    if knee_asym is not None:
        cv2.putText(frame, f"Knee Asymmetry: {knee_asym}",
                    (20, y), FONT, font_scale, (0, 0, 0), thickness + 2)
        cv2.putText(frame, f"Knee Asymmetry: {knee_asym}",
                    (20, y), FONT, font_scale, YELLOW, thickness)
        y += line_gap

    if shoulder_asym is not None:
        cv2.putText(frame, f"Shoulder Asymmetry: {shoulder_asym}",
                    (20, y), FONT, font_scale, (0, 0, 0), thickness + 2)
        cv2.putText(frame, f"Shoulder Asymmetry: {shoulder_asym}",
                    (20, y), FONT, font_scale, YELLOW, thickness)

    return frame


def draw_status(frame, analysis):
    h, w = frame.shape[:2]

    font_scale = 0.75
    thickness  = 2
    color      = GREEN if analysis["status"] == "Good" else RED

    box_height = 50 + (len(analysis["issues"]) * 36)
    cv2.rectangle(frame, (0, h - box_height - 10),
                  (w // 2, h), (0, 0, 0), -1)

    # Status with outline
    cv2.putText(frame, analysis["status"],
                (20, h - box_height + 25),
                FONT, 1.0, (0, 0, 0), thickness + 2)
    cv2.putText(frame, analysis["status"],
                (20, h - box_height + 25),
                FONT, 1.0, color, thickness)

    y = h - box_height + 58
    for issue in analysis["issues"]:
        cv2.putText(frame, f"- {issue}",
                    (20, y), FONT, font_scale, (0, 0, 0), thickness + 2)
        cv2.putText(frame, f"- {issue}",
                    (20, y), FONT, font_scale, RED, thickness)
        y += 36

    return frame