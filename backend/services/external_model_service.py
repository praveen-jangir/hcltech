
import requests
import os

class ExternalModelService:
    def __init__(self, base_url="https://30891ef1ec5d.ngrok-free.app"):
        self.base_url = base_url

    def set_base_url(self, new_url):
        """Updates the base URL for the external model."""
        self.base_url = new_url.rstrip('/')
        print(f"External Model URL updated to: {self.base_url}")

    def upload_file(self, filepath):
        url = f"{self.base_url}/upload_pdf"
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (os.path.basename(filepath), f, 'application/pdf')}
                print(f"POSTing to {url}...")
                response = requests.post(url, files=files, timeout=60)
                
                if response.status_code != 200:
                    print(f"External Upload Failed: {response.status_code} - {response.text}")
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"External Upload Exception: {e}")
            return {"error": str(e)}

    def ask_question(self, query):
        url = f"{self.base_url}/ask"
        headers = {'Content-Type': 'application/json'}
        payload = {'question': query}
        
        try:
            print(f"POSTing to {url} with query: {query}")
            response = requests.post(url, json=payload, headers=headers, timeout=60) # Increased timeout
            
            if response.status_code != 200:
                 print(f"External Ask Failed: {response.status_code} - {response.text}")

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"External Query Exception: {e}")
            return {"answer": f"External error: {str(e)}", "error": str(e)}
