import time
from wisper import OpenAiStt
import json
import sys


def load_config(file_path: str):
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Config file not found at {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in config file {file_path}")
        sys.exit(1)

def test_openai_file():
    print("\nTesting file transcription...")
    config = load_config('resources/db/config.json')
    openai = OpenAiStt(config['openai']['apikey'])
    
    start_time = time.time()
    result, err = openai.transcribe_file('/home/varashebkanthi/Downloads/harvard.wav')
    execution_time = time.time() - start_time
    
    if err:
        print(f"Error in file transcription: {err}")
    else:
        print("File transcription successful!")
        print(f"Transcript: {result}")
    print(f"Execution time: {execution_time:.2f} seconds")


def test_openai_bytes():
    print("\nTesting bytes transcription...")
    config = load_config('resources/db/config.json')
    openai = OpenAiStt(config['openai']['apikey'])

    start_time = time.time()
    with open('/home/varashebkanthi/Downloads/harvard.wav', 'rb') as audio_file:
        audio_bytes = audio_file.read()
        result, err = openai.transcribe_bytes(audio_bytes)
    execution_time = time.time() - start_time

    if err:
        print(f"Error in bytes transcription: {err}")
    else:
        print("Bytes transcription successful!")
        print(f"Transcript: {result}")
    print(f"Execution time: {execution_time:.2f} seconds")
    
def main():
    total_start_time = time.time()
    
    test_openai_file()
    test_openai_bytes()
    
    total_execution_time = time.time() - total_start_time
    print(f"\nTotal execution time: {total_execution_time:.2f} seconds")

if __name__ == "__main__":
    main()






