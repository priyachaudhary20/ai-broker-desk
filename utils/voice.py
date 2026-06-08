import tempfile

import speech_recognition as sr


def transcribe_audio(audio_file) -> dict:
    """
    Converts microphone audio into text using SpeechRecognition.

    This avoids OpenAI API usage for the demo.
    """

    try:
        recognizer = sr.Recognizer()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_file.getvalue())
            temp_audio_path = temp_audio.name

        with sr.AudioFile(temp_audio_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)

        return {
            "status": "complete",
            "text": text,
            "summary": "Voice transcription completed successfully.",
        }

    except sr.UnknownValueError:
        return {
            "status": "error",
            "text": "",
            "summary": "Voice transcription failed. Please try again.",
        }

    except sr.RequestError as e:
        return {
            "status": "error",
            "text": "",
            "summary": f"Voice transcription service failed: {str(e)}",
        }

    except Exception as e:
        return {
            "status": "error",
            "text": "",
            "summary": f"Voice transcription failed: {str(e)}",
        }