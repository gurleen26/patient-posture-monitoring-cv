import mediapipe as mp
import cv2

def get_pose_model(static_image_mode=False):
    base_options = mp.tasks.BaseOptions(
        model_asset_path='models/pose_landmarker.task'
    )
    running_mode = mp.tasks.vision.RunningMode.IMAGE if static_image_mode else mp.tasks.vision.RunningMode.VIDEO
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=running_mode,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    return mp.tasks.vision.PoseLandmarker.create_from_options(options)

def get_landmarks(results):
    if results.pose_landmarks and len(results.pose_landmarks) > 0:
        return results.pose_landmarks[0]
    return None

def draw_landmarks(frame, results):
    if not results.pose_landmarks:
        return frame
    h, w = frame.shape[:2]
    connections = [
        (0,1),(1,2),(2,3),(3,7),(0,4),(4,5),(5,6),(6,8),
        (9,10),(11,12),(11,13),(13,15),(12,14),(14,16),
        (11,23),(12,24),(23,24),(23,25),(25,27),(27,29),
        (24,26),(26,28),(28,30)
    ]
    landmarks = results.pose_landmarks[0]
    for start, end in connections:
        if start < len(landmarks) and end < len(landmarks):
            s, e = landmarks[start], landmarks[end]
            if s.visibility > 0.5 and e.visibility > 0.5:
                sx, sy = int(s.x * w), int(s.y * h)
                ex, ey = int(e.x * w), int(e.y * h)
                cv2.line(frame, (sx, sy), (ex, ey), (0, 210, 160), 2)
    for lm in landmarks:
        if lm.visibility > 0.5:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 170), -1)
    return frame