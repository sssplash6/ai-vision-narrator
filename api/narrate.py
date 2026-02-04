# File: api/narrate.py (Simplest Possible Version)

from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 1. Get API Key and prepare URL
            API_KEY = os.environ.get('GOOGLE_API_KEY')
            if not API_KEY:
                self.send_error(500, "Server configuration error: API key missing.")
                return
            
            GOOGLE_VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={API_KEY}"

            # 2. Read and parse incoming data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data)
            image_b64 = body['image'].split(',')[1]

            # 3. Prepare and send request to Google
            google_request = {
                "requests": [{
                    "image": {"content": image_b64},
                    "features": [{"type": "LABEL_DETECTION", "maxResults": 10}]
                }]
            }
            
            response = requests.post(GOOGLE_VISION_API_URL, json=google_request, timeout=10)
            response.raise_for_status()
            google_response = response.json()

            # 4. Extract and return labels
            labels = google_response['responses'][0].get('labelAnnotations', [])
            descriptions = [label['description'] for label in labels]

            # 5. Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"labels": descriptions}).encode('utf-8'))

        except Exception as e:
            # If anything fails, send a detailed error
            self.send_error(500, f"Internal Server Error: {e}")
        return
