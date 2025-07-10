import os
import logging
from typing import List, Dict, Any, AsyncGenerator
import asyncio
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel, ChatSession
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)
