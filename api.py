import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "0"
os.environ["DISPLAY"] = ""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Query, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import mediapipe as mp
import base64

from src.llm_feedback import get_ai_feedback
from src.pose import get_pose_model, get_landmarks, draw_landmarks
from src.angles import get_all_angles, reset_smoothing
from src.analyzer import analyze_posture
from src.feedback import draw_angles, draw_status
from config import MAX_WIDTH
from sessions.database import init_db, save_session

# ── App setup ──────────────────────────────────────────
app = FastAPI(title="PostureMed API")

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

@app.on_event("startup")
def startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Image endpoint ─────────────────────────────────────
@app.post("/analyse/image")
async def analyse_image(
    file: UploadFile = File(...),
    exercise: str = Query(default="standing")
):
    contents = await file.read()
    nparr    = np.frombuffer(contents, np.uint8)
    frame    = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return JSONResponse({"error": "Could not read image"}, status_code=400)

    h, w = frame.shape[:2]
    if w > MAX_WIDTH:
        scale = MAX_WIDTH / w
        frame = cv2.resize(frame, (MAX_WIDTH, int(h * scale)))

    pose     = get_pose_model(static_image_mode=True)
    rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results  = pose.detect(mp_image)
    frame    = draw_landmarks(frame, results)
    landmarks = get_landmarks(results)

    if not landmarks:
        try:
            pose.close()
        except:
            pass
        return JSONResponse({"error": "No person detected in image"}, status_code=422)

    reset_smoothing()
    angles   = get_all_angles(landmarks)
    analysis = analyze_posture(angles, exercise=exercise)
    frame    = draw_angles(frame, angles)
    frame    = draw_status(frame, analysis)

    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    img_b64   = base64.b64encode(buffer).decode('utf-8')

    try:
        pose.close()
    except:
        pass

    try:
        ai_feedback = get_ai_feedback(angles, exercise, analysis)
    except Exception as e:
        print("LLM Error:", e)
        ai_feedback = "AI feedback currently unavailable."

    save_session(exercise, analysis, angles)

    return JSONResponse({
        "angles":      angles,
        "analysis":    analysis,
        "exercise":    exercise,
        "ai_feedback": ai_feedback,
        "image":       f"data:image/jpeg;base64,{img_b64}"
    })

# ── Video endpoint ─────────────────────────────────────
@app.post("/analyse/video")
async def analyse_video(
    file: UploadFile = File(...),
    exercise: str = Query(default="standing")
):
    MAX_VIDEO_SIZE_MB = 50
    content = await file.read()
    if len(content) > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        return JSONResponse(
            {"error": f"File too large. Maximum size is {MAX_VIDEO_SIZE_MB}MB"},
            status_code=413
        )

    os.makedirs("output/temp", exist_ok=True)
    os.makedirs("output/annotated_videos", exist_ok=True)

    temp_path = f"output/temp/{file.filename}"
    out_path  = f"output/annotated_videos/annotated_{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(content)

    pose   = get_pose_model(static_image_mode=False)
    cap    = cv2.VideoCapture(temp_path)

    orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = int(cap.get(cv2.CAP_PROP_FPS)) or 30

    if orig_w > MAX_WIDTH:
        scale  = MAX_WIDTH / orig_w
        save_w = MAX_WIDTH
        save_h = int(orig_h * scale)
    else:
        save_w, save_h = orig_w, orig_h

    writer = cv2.VideoWriter(
        out_path,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps, (save_w, save_h)
    )

    timestamp     = 0
    last_angles   = {}
    last_analysis = {"status": "No person detected", "issues": []}

    reset_smoothing()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame    = cv2.resize(frame, (save_w, save_h))
        rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp += 1
        results  = pose.detect_for_video(mp_image, timestamp)
        frame    = draw_landmarks(frame, results)
        landmarks = get_landmarks(results)

        if landmarks:
            last_angles   = get_all_angles(landmarks)
            last_analysis = analyze_posture(last_angles, exercise=exercise)
            frame = draw_angles(frame, last_angles)
            frame = draw_status(frame, last_analysis)

        writer.write(frame)

    cap.release()
    writer.release()

    try:
        pose.close()
    except:
        pass

    try:
        os.remove(temp_path)
    except OSError as e:
        print(f"Could not delete temp file: {e}")

    try:
        ai_feedback = get_ai_feedback(last_angles, exercise, last_analysis)
    except Exception as e:
        print("LLM Error:", e)
        ai_feedback = "AI feedback currently unavailable."

    save_session(exercise, last_analysis, last_angles)

    return JSONResponse({
        "angles":      last_angles,
        "analysis":    last_analysis,
        "exercise":    exercise,
        "ai_feedback": ai_feedback,
        "video_url":   f"/output/annotated_videos/annotated_{file.filename}"
    })

# ── WebSocket live feed ────────────────────────────────
@app.websocket("/ws/live")
async def live_feed(websocket: WebSocket):
    await websocket.accept()
    pose      = get_pose_model(static_image_mode=False)
    exercise  = "standing"
    timestamp = 0
    reset_smoothing()

    try:
        while True:
            data = await websocket.receive_json()

            frame_bytes = base64.b64decode(data["frame"])
            nparr       = np.frombuffer(frame_bytes, np.uint8)
            frame       = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                continue

            rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp += 1
            results  = pose.detect_for_video(mp_image, timestamp)
            frame    = draw_landmarks(frame, results)
            landmarks = get_landmarks(results)

            angles   = {}
            analysis = {"status": "No person detected", "issues": []}

            if landmarks:
                angles   = get_all_angles(landmarks)
                analysis = analyze_posture(angles, exercise=exercise)
                frame    = draw_angles(frame, angles)
                frame    = draw_status(frame, analysis)

            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            img_b64   = base64.b64encode(buffer).decode('utf-8')

            await websocket.send_json({
                "image":    f"data:image/jpeg;base64,{img_b64}",
                "angles":   angles,
                "analysis": analysis
            })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        try:
            pose.close()
        except:
            pass
        reset_smoothing()

# ── Serve output files ─────────────────────────────────
app.mount("/output", StaticFiles(directory="output"), name="output")

# ── Serve frontend ─────────────────────────────────────
@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/posture_monitor.html")

app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ── Sessions endpoint ──────────────────────────────────
@app.get("/sessions")
def get_sessions():
    import sqlite3, json
    conn = sqlite3.connect("posturemed.db")
    rows = conn.execute(
        "SELECT id, timestamp, exercise, status, angles, issues FROM sessions ORDER BY id DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [
        {
            "id":        r[0],
            "timestamp": r[1],
            "exercise":  r[2],
            "status":    r[3],
            "angles":    json.loads(r[4]),
            "issues":    json.loads(r[5])
        }
        for r in rows
    ]