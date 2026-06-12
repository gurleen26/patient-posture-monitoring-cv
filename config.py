# =============================================================
# PostureMed — Configuration File
# =============================================================

# ── Camera settings ───────────────────────────────────────────
CAMERA_INDEX  = 0
FRAME_WIDTH   = 1280
FRAME_HEIGHT  = 720
FPS           = 30
MAX_WIDTH     = 1280   # max resolution for processing

# ── MediaPipe settings ────────────────────────────────────────
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE  = 0.5
LANDMARK_VISIBILITY_MIN  = 0.5   # skip landmarks below this confidence

# ── Smoothing ─────────────────────────────────────────────────
SMOOTHING_BUFFER_SIZE = 8   # number of frames to average angles over

# ── Asymmetry threshold ───────────────────────────────────────
ASYMMETRY_THRESHOLD = 15    # degrees difference between left and right side

# ── Default standing posture thresholds ───────────────────────
KNEE_ANGLE_MIN     = 160
KNEE_ANGLE_MAX     = 180
SPINE_ANGLE_MIN    = 150
SHOULDER_ANGLE_MIN = 20

# ── Exercise specific thresholds ──────────────────────────────
# Each exercise defines safe angle ranges for knee, spine, shoulder
# Add more exercises here as your project grows

EXERCISES = {

    "standing": {
        "description":    "Normal standing posture",
        "knee_min":       100,
        "knee_max":       180,
        "spine_min":      155,
        "shoulder_min":   15,
        "asymmetry_threshold": 15,
    },

    "squat": {
        "description":    "Basic squat — knees should be at 80–100 degrees",
        "knee_min":       70,
        "knee_max":       110,
        "spine_min":      140,
        "shoulder_min":   15,
        "asymmetry_threshold": 15,
    },

    "lunge": {
        "description":    "Forward lunge — front knee at 80–100 degrees",
        "knee_min":       75,
        "knee_max":       105,
        "spine_min":      150,
        "shoulder_min":   15,
    },

    "shoulder_raise": {
        "description":    "Lateral shoulder raise — arm to shoulder height",
        "knee_min":       155,
        "knee_max":       180,
        "spine_min":      160,
        "shoulder_min":   75,
    },

    "bridge": {
        "description":    "Glute bridge — hips raised off floor",
        "knee_min":       80,
        "knee_max":       110,
        "spine_min":      120,
        "shoulder_min":   15,
    },

    "warrior": {
        "description":    "Warrior balance pose — forward lean expected",
        "knee_min":       155,
        "knee_max":       180,
        "spine_min":      100,
        "shoulder_min":   60,
    },
}

# ── Default exercise to use ────────────────────────────────────
# Change this to switch exercise context
DEFAULT_EXERCISE = "standing"

# ── Output paths ──────────────────────────────────────────────
OUTPUT_IMAGES = "output/annotated_images"
OUTPUT_VIDEOS = "output/annotated_videos"
OUTPUT_TEMP   = "output/temp"