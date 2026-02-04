# File: api/narrate.py

import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

MODEL_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

@app.post("/")
async def narrate_image(request: Request):
    logger.info("--- API function starting ---")
    try:
        HF_TOKEN = os.environ.get('HF_TOKEN')
        if not HF_TOKEN:
            logger.error("!!! CRITICAL: HF_TOKEN not found.")
            return JSONResponse(status_code=500, content={"error": "Server is not configured."})
        
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        # Expect a JSON body with a base64 string
        body = await request.json()
        image_base64_string = body['image'].split(',')[1]
        
        # Decode the base64 string back into bytes
        image_bytes = base64.b64decode(image_base64_string)
        logger.info(f"Successfully decoded image data, size: {len(image_bytes)} bytes.")
        
        logger.info("Sending request to Hugging Face API...")
        response = requests.post(MODEL_URL, headers=headers, data=image_bytes, timeout=20)
        
        logger.info(f"Hugging Face API Response Status: {response.status_code}")
        response.raise_for_status()
        
        hf_response = response.json()
        logger.info(f"Hugging Face Response Body: {hf_response}")

        caption = hf_response[0].get('generated_text', 'No description found.')
        logger.info(f"Extracted caption: {caption}")
        
        return JSONResponse(status_code=200, content={"caption": caption})

    except Exception as e:
        logger.error(f"!!! An unexpected error occurred: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "An internal server error occurred."})
