import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def get_pose_model(static_image_mode=False):
    return mp_pose.Pose(
        static_image_mode=static_image_mode,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )


def get_landmarks(results):
    if results.pose_landmarks:
        return results.pose_landmarks.landmark
    return None


def draw_landmarks(frame, results):
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    return frame