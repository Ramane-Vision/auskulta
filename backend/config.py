import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", None)

VISUAL_ANOMALY_THRESHOLD = float(os.getenv("VISUAL_ANOMALY_THRESHOLD", "0.55"))
AUDIO_ANOMALY_THRESHOLD = float(os.getenv("AUDIO_ANOMALY_THRESHOLD", "0.55"))
