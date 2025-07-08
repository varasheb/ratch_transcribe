import requests
from pathlib import Path

class DeepgramStt:
    BASE_URL = "https://api.deepgram.com/v1/listen"
    
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise ValueError("API key Not Found")
        
        self.api_key = api_key.strip()
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }    
        
    def transcribe_file(self, file_path: str) -> tuple:
        try:
            # Convert to Path object and validate
            audio_path = Path(file_path)
            if not audio_path.exists():
                return None, f"Audio file not found: {file_path}"
            
            # Prepare API request
            url = self.BASE_URL
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": f"audio/{audio_path.suffix[1:]}"
            }
            
            # Simple parameters for fast transcription
            params = {
                'model': 'nova-2',
                'language': 'en',
                'punctuate': 'true',
                'smart_format': 'true'
            }
            
            # Read and send audio file
            with open(audio_path, 'rb') as audio_file:
                response = requests.post(
                    url,
                    headers=headers,
                    params=params,
                    data=audio_file.read()
                )
            
            # Check response
            if response.status_code != 200:
                return None, f"API error: {response.text}"
            
            # Parse response and extract text
            result = response.json()
            channels = result.get('results', {}).get('channels', [])
            
            if channels and channels[0].get('alternatives'):
                transcript = channels[0]['alternatives'][0].get('transcript', '').strip()
                return transcript, None
            
            return "", None
            
        except Exception as e:
            return None, f"Transcription failed: {str(e)}"
        
    def transcribe_bytes(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> tuple:
        try:
            url = self.BASE_URL
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": mime_type
            }
            
            params = {
                'model': 'nova-2',
                'language': 'en',
                'punctuate': 'true',
                'smart_format': 'true'
            }
            
            response = requests.post(
                url,
                headers=headers,
                params=params,
                data=audio_bytes
            )
            
            if response.status_code != 200:
                return None, f"API error: {response.text}"
            
            result = response.json()
            channels = result.get('results', {}).get('channels', [])
            
            if channels and channels[0].get('alternatives'):
                transcript = channels[0]['alternatives'][0].get('transcript', '').strip()
                return transcript, None
            
            return "", None
            
        except Exception as e:
            return None, f"Transcription failed: {str(e)}"
        
    