import os

# --- Application Settings ---

# --- Class Definitions (YOLO-World Open Vocabulary) ---

# 1. DOMESTIC & SAFE (Green)
DOMESTIC_SAFE_ANIMALS = {
    "domestic cat": "cat",
    "pet dog": "dog",
    "horse": "horse",
    "cow": "cow",
    "sheep": "sheep",
    "pig": "pig",
    "goat": "goat",
    "chicken": "chicken",
    "person": "person"
}

# 2. WILD & SAFE (Yellow)
WILD_SAFE_ANIMALS = {
    "zebra": "zebra",
    "giraffe": "giraffe",
    "bird": "bird",
    "deer": "deer",
    "monkey": "monkey",
    "rabbit": "rabbit",
    "squirrel": "squirrel",
}

# 3. WILD & DANGEROUS (Red - TRIGGER ALERT)
WILD_DANGEROUS_ANIMALS = {
    "tiger": "tiger",
    "lion": "lion",
    "cheetah": "cheetah",
    "leopard": "leopard",
    "bear": "bear",
    "elephant": "elephant",
    "wolf": "wolf",
    "fox": "fox",
    "hyena": "hyena",
    "crocodile": "crocodile",
    "snake": "snake"
}

# Combine all keys for the model's vocabulary
ANIMAL_VOCABULARY = list(DOMESTIC_SAFE_ANIMALS.keys()) + \
                    list(WILD_SAFE_ANIMALS.keys()) + \
                    list(WILD_DANGEROUS_ANIMALS.keys())

# Flat lists for simple lookup (useful for custom model)
WILD_DANGEROUS_NAMES = list(WILD_DANGEROUS_ANIMALS.values())
WILD_SAFE_NAMES = list(WILD_SAFE_ANIMALS.values())
DOMESTIC_SAFE_NAMES = list(DOMESTIC_SAFE_ANIMALS.values())

CONFIDENCE_THRESHOLD = 0.20 # Lower for broader detection
DANGER_CONFIDENCE_MIN = 0.20 # Stay alert for danger
SAFE_CONFIDENCE_MIN = 0.30   # Lowered from 0.40 to capture 'person' more reliably

# --- Performance Optimization ---
FRAME_SKIP = 3        # Process every 3rd frame (higher = faster but less reactive)
DETECTION_WIDTH = 416 # Resize frame to this width for inference (lower = faster)

# --- Alert Settings ---

# Cooldown in seconds to prevent spamming
SOUND_COOLDOWN = 10
NOTIFICATION_COOLDOWN = 60 # Email/SMS every 60 seconds max

# --- Notification Credentials ---

# Select Notification Method: 'EMAIL', 'SMS', or 'BOTH'
NOTIFICATION_METHOD = 'EMAIL' 

# Email Settings (Gmail example: use App Password)
SENDER_EMAIL = "sumankamatar@gmail.com"
SENDER_PASSWORD = "hnpfvqsspmkapooi"
RECIPIENT_EMAIL = "pmajor159@gmail.com"

# Twilio Settings (if using SMS)
TWILIO_ACCOUNT_SID = "ACxxxxxxxx"
TWILIO_AUTH_TOKEN = "xxxxxxxx"
TWILIO_PHONE_NUMBER = "+1234567890"
RECIPIENT_PHONE_NUMBER = "+0987654321"

# Alert Sound File
ALERT_SOUND_PATH = "alert.wav"
