import speech_recognition as sr
import edge_tts
import pygame
import os
import time
import tempfile
import threading
import queue
from config import TTS_VOICE

# Initialize pygame mixer once globally
try:
    pygame.mixer.init()
except Exception:
    pass

# Use a temp file outside the project folder to avoid file locking

# Base temp dir for TTS files
_TTS_DIR = tempfile.gettempdir()
_speak_idx = 0

_tts_queue = queue.Queue()
_tts_thread = None
_stop_event = threading.Event()

def _tts_worker():
    file_idx = 0
    while True:
        text = _tts_queue.get()
        if text is None:
            break
            
        if _stop_event.is_set():
            _tts_queue.task_done()
            continue
            
        temp_file = os.path.join(tempfile.gettempdir(), f"rubiks_tts_stream_{file_idx}.mp3")
        file_idx += 1
        
        try:
            communicate = edge_tts.Communicate(text, TTS_VOICE, rate='+15%')
            communicate.save_sync(temp_file)
            
            if not _stop_event.is_set():
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy() and not _stop_event.is_set():
                    time.sleep(0.05)
                    
                if _stop_event.is_set():
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
        except Exception as e:
            print(f"[TTS Error] {e}")
            
        _tts_queue.task_done()

def start_tts_engine():
    global _tts_thread
    if _tts_thread is None or not _tts_thread.is_alive():
        _tts_thread = threading.Thread(target=_tts_worker, daemon=True)
        _tts_thread.start()

def stream_speak(text: str):
    """Adds a sentence to the TTS queue to be spoken immediately."""
    _stop_event.clear()
    clean_text = text.replace('*', '').replace('`', '').replace('#', '').strip()
    if clean_text:
        _tts_queue.put(clean_text)

def stop_speaking():
    """Stops pygame audio playback instantly and clears the queue."""
    _stop_event.set()
    try:
        if pygame.mixer.get_init():
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.unload()
    except Exception:
        pass
    
    # clear queue
    while not _tts_queue.empty():
        try:
            _tts_queue.get_nowait()
            _tts_queue.task_done()
        except queue.Empty:
            break

def speak(text: str):
    """Converts text to speech and plays it asynchronously using pygame."""
    
    # Strip markdown symbols so the TTS doesn't read "asterisk asterisk"
    clean_text = text.replace('*', '').replace('`', '').replace('#', '')
    
    global _speak_idx
    _speak_idx += 1
    temp_file = os.path.join(_TTS_DIR, f"rubiks_tts_speak_{_speak_idx}.mp3")
    try:
        # Instantly kill any currently playing speech to unlock the file
        stop_speaking()
        
        # edge-tts v7+ has a synchronous save method.
        # Rate +15% to make the voice sound natural and conversational (default is too slow).
        communicate = edge_tts.Communicate(clean_text, TTS_VOICE, rate='+15%')
        communicate.save_sync(temp_file)

        # Play the generated audio file
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # We intentionally DO NOT wait for playback to finish, so the user can keep typing/talking.
    except Exception as e:
        print(f"[TTS Error] {e}")


def list_microphones() -> list:
    """Lists all available microphones."""
    return sr.Microphone.list_microphone_names()


def listen(mic_index: int = None, timeout: int = 7, phrase_limit: int = 15) -> str:
    """Listens to the microphone and returns the transcribed text."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    # Lowered pause_threshold for faster response
    recognizer.pause_threshold = 0.4
    recognizer.non_speaking_duration = 0.3

    try:
        if mic_index is not None:
            mic = sr.Microphone(device_index=mic_index)
        else:
            mic = sr.Microphone()

        with mic as source:
            # Lowered duration from 0.8 to 0.2 so it starts listening almost instantly
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = recognizer.recognize_google(audio)
            return text.strip()
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return "[ERROR] Google Speech Recognition service unavailable."
    except OSError as e:
        return f"[ERROR] Microphone error: {e}"
    except Exception as e:
        return f"[ERROR] {e}"
