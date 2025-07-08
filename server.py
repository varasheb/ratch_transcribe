from svc.deepgramsvc.deepgram import DeepgramStt
from svc.openaisvc.wisper import OpenAiStt
from svc.livekitsvc.agent import MyAgent
import json
import argparse

def init_config():
    try:
        # take config from arguments
        parser = argparse.ArgumentParser(description='Deepgram Transcription Server')
        parser.add_argument('--configfile', '-c', 
                       required=True,
                       help='Path to the configuration JSON file')
        args = parser.parse_args()
        config_file_path = args.configfile
        with open(config_file_path, 'r') as config_file:
            return json.load(config_file)
            
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in config file: {e}")


def main():
    config = init_config()

    agent = MyAgent(
        openai_api_key=config['openai']['apikey'], 
        livekit_api_key=config['livekit']['apikey'], 
        livekit_api_secret=config['livekit']['secretkey'], 
        livekit_url=config['livekit']['host']
    )
    agent.run()
 


if __name__ == "__main__":
    main()

