# File: api/narrate.py (Final FastAPI Version)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import requests

# Vercel will automatically find and run this 'app' object.
app = FastAPI()

# This decorator tells FastAPI to handle POST requests that are routed to this file.
# Since the file is named narrate.py, the full URL becomes /api/narrate
@app.post("/")
async def narrate_image(request: Request):
    # 1. Securely get the API Key from Vercel's environment variables
    API_KEY = os.environ.get('GOOGLE_API_KEY')
    if not API_KEY:
        return JSONResponse(status_code=500, content={"error": "API key is not configured."})
    
    GOOGLE_VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

    # 2. Read the image data sent from the frontend
    try:
        body = await request.json()
        # The frontend sends a string like "data:image/jpeg;base64,..."
        # We need to get only the part after the comma.
        image_b64 = body['image'].split(',')[1]
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid image data received."})

    # 3. Construct the request payload for Google's AI model
    google_request = {
        "requests": [{
            "image": {"content": image_b64},
            "features": [{"type": "LABEL_DETECTION", "maxResults": 10}]
        }]
    }

    # 4. Call the Google Vision AI API
    try:
        response = requests.post(GOOGLE_VISION_API_URL, json=google_request)
        response.raise_for_status() # This will raise an error for bad responses (like 4xx or 5xx)
        google_response = response.json()
        
        if 'responses' not in google_response or not google_response['responses']:
            raise ValueError("Invalid response structure from Google Vision API")

        # 5. Process the AI's response and send it back to our frontend
        labels = google_response['responses'][0].get('labelAnnotations', [])
        descriptions = [label['description'] for label in labels]
        
        return JSONResponse(status_code=200, content={"labels": descriptions})

    except Exception as e:
        # If anything goes wrong, return a server error with the details
        return JSONResponse(status_code=500, content={"error": str(e)})
