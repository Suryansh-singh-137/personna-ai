from elevenlabs import ElevenLabs, VoiceSettings
from dotenv import load_dotenv
import pygame
import io
import os

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Rachel — warm, natural, emotional. Best for companion use case.
# You can change this to any voice ID from elevenlabs.io/voices
VOICE_ID = "o6qTxWUeRyzRYZyUNDVJ"

def speak(text: str):
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_turbo_v2_5",  # fastest model, low latency
        voice_settings=VoiceSettings(
            stability=0.4,        # lower = more expressive/emotional
            similarity_boost=0.8, # how closely it matches the voice
            style=0.5,            # style exaggeration
            use_speaker_boost=True
        )
    )

    # convert generator to bytes
    audio_bytes = b"".join(audio)
    
    # play using pygame
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(audio_bytes), "mp3")
    pygame.mixer.music.play()
    
    # wait for audio to finish before returning
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)