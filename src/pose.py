import mediapipe as mp
import cv2
import numpy as np

PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
BaseOptions = mp.tasks.BaseOptions

import urllib.request
import os

MODEL_PATH = "models/pose_landmarker.task"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading pose model...")
        url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
        os.makedirs("models", exist_ok=True)
        urllib.request.urlretrieve(url, MODEL_PATH)
        print("Model downloaded.")

def get_pose_model(static_image_mode=False):
    download_model()
    mode = VisionRunningMode.IMAGE if static_image_mode else VisionRunningMode.VIDEO
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=mode
    )
    return PoseLandmarker.create_from_options(options)

def get_landmarks(results):
    if results.pose_landmarks and len(results.pose_landmarks) > 0:
        return results.pose_landmarks[0]
    return None

def draw_landmarks(frame, results):
    if not results.pose_landmarks or len(results.pose_landmarks) == 0:
        return frame

    h, w = frame.shape[:2]
    landmarks = results.pose_landmarks[0]

    connections = [
        (0,1),(1,2),(2,3),(3,7),(0,4),(4,5),(5,6),(6,8),
        (9,10),(11,12),(11,13),(13,15),(12,14),(14,16),
        (11,23),(12,24),(23,24),(23,25),(24,26),(25,27),(26,28),
        (27,29),(28,30),(29,31),(30,32)
    ]

    points = {}
    for i, lm in enumerate(landmarks):
        cx, cy = int(lm.x * w), int(lm.y * h)
        points[i] = (cx, cy)
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

    for a, b in connections:
        if a in points and b in points:
            cv2.line(frame, points[a], points[b], (255, 255, 0), 2)

    return frame