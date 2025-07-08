import requests
from pathlib import Path

class OpenAiStt:
    BASE_URL = "https://api.openai.com/v1/audio/transcriptions"
    
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise ValueError("API key Not Found")
        
        self.api_key = api_key.strip()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def transcribe_file(self, file_path: str) -> tuple:
        try:
            audio_path = Path(file_path)
            if not audio_path.exists():
                return None, f"Audio file not found: {file_path}"
            
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': (audio_path.name, audio_file, f'audio/{audio_path.suffix[1:]}')
                }
                data = {
                    'model': 'whisper-1',
                    'language': 'en',
                    'response_format': 'json'
                }
                
                response = requests.post(
                    self.BASE_URL,
                    headers=self.headers,
                    files=files,
                    data=data
                )
            
            if response.status_code != 200:
                return None, f"API error: {response.text}"
            
            result = response.json()
            transcript = result.get('text', '').strip()
            return transcript, None
            
        except Exception as e:
            return None, f"Transcription failed: {str(e)}"
    
    def transcribe_bytes(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> tuple:
        try:
            files = {
                'file': ('audio', audio_bytes, mime_type)
            }
            data = {
                'model': 'whisper-1',
                'language': 'en',
                'response_format': 'json'
            }
            
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                files=files,
                data=data
            )
            
            if response.status_code != 200:
                return None, f"API error: {response.text}"
            
            result = response.json()
            transcript = result.get('text', '').strip()
            return transcript, None
            
        except Exception as e:
            return None, f"Transcription failed: {str(e)}"
