import azure.cognitiveservices.speech as speechsdk
from fastapi import HTTPException
import os

def synthesize_speech(text: str) -> bytes:
    
    print("[TTS] Starting speech synthesis...")
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION"),
        )
        speech_config.speech_synthesis_voice_name = "en-US-RyanMultilingualNeural"

        # Use an in-memory stream to capture WAV output
        audio_stream = speechsdk.audio.AudioOutputConfig(filename="report.wav")  # temporary file
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_stream
        )

        result = synthesizer.speak_text_async(text).get()
        print(f"[TTS] Synthesis completed with reason: {result.reason}")

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # read the file bytes
            with open("report.wav", "rb") as f:
                audio_bytes = f.read()
            print("[TTS] Audio bytes length:", len(audio_bytes))
            return audio_bytes

        elif result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details
            raise HTTPException(
                status_code=500,
                detail=f"TTS canceled: {details.reason} - {details.error_details}",
            )

    except Exception as e:
        print("[TTS] Exception occurred:", str(e))
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")