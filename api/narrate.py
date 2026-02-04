# File: api/narrate.py (Hugging Face Version)

import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# This is the Hugging Face model we will use. It's great for general image captioning.
MODEL_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

@app.post("/")
async def narrate_image(request: Request):
    logger.info("--- API function starting ---")
    try:
        # 1. Get Hugging Face Token from Vercel's environment variables
        HF_TOKEN = os.environ.get('HF_TOKEN')
        if not HF_TOKEN:
            logger.error("!!! CRITICAL: HF_TOKEN not found.")
            return JSONResponse(status_code=500, content={"error": "Server is not configured."})
        
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        logger.info("Hugging Face token loaded.")

        # 2. Read the raw image data (as bytes)
        image_bytes = await request.body()
        logger.info(f"Successfully received image data, size: {len(image_bytes)} bytes.")
        
        # 3. Call the Hugging Face Inference API
        logger.info("Sending request to Hugging Face API...")
        response = requests.post(MODEL_URL, headers=headers, data=image_bytes, timeout=20)
        
        logger.info(f"Hugging Face API Response Status: {response.status_code}")
        
        response.raise_for_status() # Raise an error for bad status codes
        
        hf_response = response.json()
        logger.info(f"Hugging Face Response Body: {hf_response}")

        # 4. Extract the generated caption
        if isinstance(hf_response, list) and hf_response:
            # The model returns a list with a dictionary, e.g., [{'generated_text': 'a dog playing in a park'}]
            caption = hf_response[0].get('generated_text', 'No description found.')
        else:
            raise ValueError("Invalid response structure from Hugging Face API")

        # 5. Send the caption back to the frontend
        logger.info(f"Extracted caption: {caption}")
        return JSONResponse(status_code=200, content={"caption": caption})

    except requests.exceptions.RequestException as e:
        logger.error(f"!!! HTTP Request ERROR: {e}")
        if e.response is not None:
            logger.error(f"Hugging Face's Error Response: {e.response.text}")
        return JSONResponse(status_code=500, content={"error": f"Failed to communicate with Hugging Face API: {e}"})

    except Exception as e:
        logger.error(f"!!! An unexpected error occurred: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "An internal server error occurred."})

