import numpy as np
from collections import deque

LANDMARK = {
    "nose": 0,
    "left_shoulder": 11,  "right_shoulder": 12,
    "left_elbow": 13,     "right_elbow": 14,
    "left_wrist": 15,     "right_wrist": 16,
    "left_hip": 23,       "right_hip": 24,
    "left_knee": 25,      "right_knee": 26,
    "left_ankle": 27,     "right_ankle": 28
}

# Smoothing buffer
_angle_buffer = deque(maxlen=8)


def calculate_angle(a, b, c):
    """
    Calculate angle at point b between vectors ba and bc.
    """
    a, b, c = np.array(a), np.array(b), np.array(c)

    ba = a - b
    bc = c - b

    cosine = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6
    )

    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    return round(angle, 1)


def calculate_spine_angle(shoulder, hip):
    """
    Measures torso inclination relative to vertical axis.

    180° = perfectly upright
    lower values = more leaning
    """

    shoulder = np.array(shoulder[:2])
    hip = np.array(hip[:2])

    torso_vector = shoulder - hip

    # Perfect vertical upward direction
    vertical_vector = np.array([0, -1])

    cosine = np.dot(torso_vector, vertical_vector) / (
        np.linalg.norm(torso_vector) *
        np.linalg.norm(vertical_vector) + 1e-6
    )

    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    # Convert into uprightness score
    spine_angle = 180 - angle

    return round(spine_angle, 1)


def get_coord(landmarks, name, use_3d=False):
    """
    Get landmark coordinates.
    Returns None if landmark visibility is low.
    """

    lm = landmarks[LANDMARK[name]]

    if hasattr(lm, 'visibility') and lm.visibility < 0.5:
        return None

    if use_3d:
        return [lm.x, lm.y, lm.z]

    return [lm.x, lm.y]


def smooth_angles(new_angles):
    """
    Smooth angle values over last few frames.
    """

    _angle_buffer.append(new_angles)

    smoothed = {}

    for key in new_angles:

        values = [
            frame[key]
            for frame in _angle_buffer
            if frame.get(key) is not None
        ]

        smoothed[key] = (
            round(sum(values) / len(values), 1)
            if values else None
        )

    return smoothed


def get_all_angles(landmarks):

    angles = {}

    # ==================================================
    # LEFT SIDE
    # ==================================================

    lh = get_coord(landmarks, "left_hip")
    lk = get_coord(landmarks, "left_knee")
    la = get_coord(landmarks, "left_ankle")

    ls = get_coord(landmarks, "left_shoulder")
    le = get_coord(landmarks, "left_elbow")

    # Left knee
    if all(v is not None for v in [lh, lk, la]):
        angles["left_knee"] = calculate_angle(lh, lk, la)

    # Spine
    if all(v is not None for v in [ls, lh]):
        angles["spine"] = calculate_spine_angle(ls, lh)

    # Shoulder
    lw = get_coord(landmarks, "left_wrist")
    rs = get_coord(landmarks, "right_shoulder")

    if all(v is not None for v in [lw, ls, rs]):
        angles["shoulder"] = calculate_angle(lw, ls, rs)

    # ==================================================
    # RIGHT SIDE
    # ==================================================

    rh = get_coord(landmarks, "right_hip")
    rk = get_coord(landmarks, "right_knee")
    ra = get_coord(landmarks, "right_ankle")

    rs = get_coord(landmarks, "right_shoulder")
    re = get_coord(landmarks, "right_elbow")

    # Right knee
    if all(v is not None for v in [rh, rk, ra]):
        angles["right_knee"] = calculate_angle(rh, rk, ra)

    # Right spine
    if all(v is not None for v in [rs, rh]):
        angles["right_spine"] = calculate_spine_angle(rs, rh)

    # Right shoulder
    rw = get_coord(landmarks, "right_wrist")
    ls = get_coord(landmarks, "left_shoulder")

    if all(v is not None for v in [rw, rs, ls]):
        angles["right_shoulder"] = calculate_angle(rw, rs, ls)

    # ==================================================
    # ASYMMETRY
    # ==================================================

    if "left_knee" in angles and "right_knee" in angles:
        angles["knee_asymmetry"] = round(
            abs(angles["left_knee"] - angles["right_knee"]),
            1
        )

    if "shoulder" in angles and "right_shoulder" in angles:
        angles["shoulder_asymmetry"] = round(
            abs(angles["shoulder"] - angles["right_shoulder"]),
            1
        )

    # ==================================================
    # SMOOTHING
    # ==================================================

    angles = smooth_angles(angles)

    return angles


def reset_smoothing():
    """
    Reset smoothing buffer when starting new session.
    """
    _angle_buffer.clear()