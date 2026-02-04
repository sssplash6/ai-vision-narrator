# File: api/narrate.py (Final Debugging & Fix Version)

import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

# Set up a logger to capture all output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/")
async def narrate_image(request: Request):
    logger.info("--- API function starting ---")
    try:
        # 1. Check for API Key
        API_KEY = os.environ.get('GOOGLE_API_KEY')
        if not API_KEY:
            logger.error("!!! CRITICAL: GOOGLE_API_KEY not found.")
            return JSONResponse(status_code=500, content={"error": "Server is not configured."})
        
        logger.info("API Key found.")
        GOOGLE_VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

        # 2. Read and parse incoming data
        body = await request.json()
        image_b64 = body['image'].split(',')[1]
        logger.info("Successfully parsed image data from request.")

        # 3. Prepare payload for Google Vision API
        google_request = {
            "requests": [{
                "image": {"content": image_b64},
                "features": [{"type": "LABEL_DETECTION", "maxResults": 10}]
            }]
        }

        # 4. Make the request to Google Vision API
        logger.info("Sending request to Google Vision API...")
        response = requests.post(GOOGLE_VISION_API_URL, json=google_request, timeout=10)
        
        logger.info(f"Google API Response Status: {response.status_code}")
        
        # This will raise an error if the status code is 4xx or 5xx
        response.raise_for_status()
        
        google_response = response.json()
        logger.info("Successfully received and parsed JSON response from Google.")

        # 5. Extract labels and return response
        labels = google_response.get('responses', [])[0].get('labelAnnotations', [])
        descriptions = [label['description'] for label in labels]
        logger.info(f"Extracted labels: {descriptions}")

        return JSONResponse(status_code=200, content={"labels": descriptions})

    except requests.exceptions.RequestException as e:
        logger.error(f"!!! HTTP Request ERROR: {e}")
        # Log the full response body if it exists, as it often contains the error message from Google
        if e.response is not None:
            logger.error(f"Google's Error Response: {e.response.text}")
        return JSONResponse(status_code=500, content={"error": f"Failed to communicate with Google Vision API: {e}"})

    except Exception as e:
        # This is a catch-all for any other error (e.g., parsing, key errors)
        logger.error(f"!!! An unexpected error occurred: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "An internal server error occurred."})

