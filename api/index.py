from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel expects the app to be available as 'app' variable
# The main.py already exports the FastAPI app, so we just import it

# Export for Vercel - both 'app' and 'handler' for compatibility
handler = app
