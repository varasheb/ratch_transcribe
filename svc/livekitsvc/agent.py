import asyncio
from livekit import agents, rtc
from livekit.agents.stt import SpeechEventType, SpeechEvent
from typing import AsyncIterable, Dict
from livekit.plugins import openai


class MyAgent:
    def __init__(self, openai_api_key: str, livekit_api_key: str, livekit_api_secret: str, livekit_url: str):
        self.openai_api_key = openai_api_key
        self.livekit_api_key = livekit_api_key
        self.livekit_api_secret = livekit_api_secret
        self.livekit_url = livekit_url
        self.participants: Dict[str, str] = {}
        self.run()
        
    def run(self):
        # Create worker options with LiveKit credentials
        worker_options = agents.WorkerOptions(
            entrypoint_fnc=self.entrypoint,
            api_key=self.livekit_api_key,
            api_secret=self.livekit_api_secret,
            ws_url=self.livekit_url
        )
        agents.cli.run_app(worker_options)
        
    async def entrypoint(self, ctx: agents.JobContext):
        await ctx.connect()
        
        # Get room information
        room_id = ctx.room.name
        room_sid = ctx.room.sid
        print(f"🏠 Connected to room: {room_id} (SID: {room_sid})")
        print(f"🏠 Room URL: {self.livekit_url}")

        # Track participants for username mapping
        @ctx.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):  # noqa: F841
            self.participants[participant.identity] = participant.name or participant.identity
            print(participant)
            print(f"👤 Participant connected: {self.participants[participant.identity]} (ID: {participant.identity})")
            print(f"👤 Room ID: {room_id}")

        @ctx.room.on("participant_disconnected")
        def on_participant_disconnected(participant: rtc.RemoteParticipant):  # noqa: F841
            participant_name = self.participants.get(participant.identity, participant.identity)
            print(f"👋 Participant disconnected: {participant_name}")
            print(f"👋 Room ID: {room_id}")
            if participant.identity in self.participants:
                del self.participants[participant.identity]

        @ctx.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.RemoteTrack, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):  # noqa: F841
            participant_name = participant.name or participant.identity
            self.participants[participant.identity] = participant_name
            print(f"🎵 Subscribed to track: {track.name} from {participant_name}")
            print(f"🎵 Room ID: {room_id}")
            asyncio.create_task(self.process_track(track, participant))

    async def process_track(self, track: rtc.RemoteTrack, participant: rtc.RemoteParticipant):
        # Initialize STT with OpenAI Whisper - pass API key directly
        stt = openai.STT(
            model="whisper-1",
            language="en",
            api_key=self.openai_api_key  # Pass API key directly
        )
        stt_stream = stt.stream()
        audio_stream = rtc.AudioStream(track)

        # Create task for processing STT stream
        stt_task = asyncio.create_task(self.process_stt_stream(stt_stream, participant))

        try:
            # Process audio stream
            async for audio_event in audio_stream:
                stt_stream.push_frame(audio_event.frame)

            # End audio stream
            stt_stream.end_input()

            # Wait for STT processing to complete
            await stt_task
        except Exception as e:
            print(f"Error processing track: {e}")
            stt_task.cancel()
            try:
                await stt_task
            except asyncio.CancelledError:
                pass

    async def process_stt_stream(self, stream: AsyncIterable[SpeechEvent], participant: rtc.RemoteParticipant):
        participant_name = self.participants.get(participant.identity, participant.name or participant.identity)
        print(f"🎤 Processing audio for participant: {participant_name}")
        
        try:
            async for event in stream:
                if event.type == SpeechEventType.FINAL_TRANSCRIPT:
                    print(f"FULL Event: {event}")
                    
                    # Get speaker information
                    speaker_info = ""
                    if event.alternatives and len(event.alternatives) > 0:
                        alternative = event.alternatives[0]
                        
                        if hasattr(alternative, 'speaker_id') and alternative.speaker_id is not None:
                            speaker_info = f"[Speaker {alternative.speaker_id}] {participant_name}"
                        else:
                            speaker_info = f"[{participant_name}]"
                        
                        # Format timestamp
                        timestamp = ""
                        if hasattr(alternative, 'start_time') and alternative.start_time is not None:
                            timestamp = f"[{alternative.start_time:.2f}s] "
                        
                        print(f"🎤 {timestamp}{speaker_info}: {alternative.text}")
                    else:
                        print(f"🎤 [{participant_name}]: {event.alternatives[0].text if event.alternatives else 'No text'}")
                        
                elif event.type == SpeechEventType.INTERIM_TRANSCRIPT:
                    if event.alternatives and len(event.alternatives) > 0:
                        print(f"💭 [{participant_name}] (interim): {event.alternatives[0].text}")
                elif event.type == SpeechEventType.START_OF_SPEECH:
                    print(f"🗣️  [{participant_name}] Start of speech")
                elif event.type == SpeechEventType.END_OF_SPEECH:
                    print(f"🔇 [{participant_name}] End of speech")
        except Exception as e:
            print(f"Error processing STT stream for {participant_name}: {e}")



if __name__ == "__main__":
  pass