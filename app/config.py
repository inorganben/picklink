#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "")
BASE_URL = os.getenv("BASE_URL", "")
