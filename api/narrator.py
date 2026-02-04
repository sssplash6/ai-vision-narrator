# File: api/narrate.py

from http.server import BaseHTTPRequestHandler
import json
import os
import requests

# This is the main function Vercel's Python runtime will execute.
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Get the API Key and prepare the Google Vision API URL
        # os.environ.get() securely reads the environment variable we set in the Vercel dashboard.
        API_KEY = os.environ.get('GOOGLE_API_KEY')
        if not API_KEY:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "API key is not configured."}).encode('utf-8'))
            return
            
        GOOGLE_VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

        # 2. Read the image data sent from the frontend
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            # The frontend will send a JSON payload like: {"image": "data:image/jpeg;base64,..."}
            body = json.loads(post_data)
            # We need to strip the "data:image/jpeg;base64," part to get the raw image data
            image_b64 = body['image'].split(',')[1]
        except Exception:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid image data received."}).encode('utf-8'))
            return

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
            response.raise_for_status() # This will raise an error if the request fails
            google_response = response.json()
            
            # 5. Process the AI's response
            if 'responses' not in google_response or not google_response['responses']:
                 raise ValueError("Invalid response from Google Vision API")

            # Extract the text descriptions of the labels found in the image
            labels = google_response['responses'][0].get('labelAnnotations', [])
            descriptions = [label['description'] for label in labels]

            # 6. Send the clean list of labels back to our frontend
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"labels": descriptions}).encode('utf-8'))

        except Exception as e:
            # Send a generic error if anything goes wrong
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return
