"""
Growth OS - Focus & Cognitive Audio Engine
Synthesizes 40Hz Gamma Isochronic waves and Deep Brown Noise directly into memory
using the native Windows multimedia subsystem (winsound PlaySound async loop).
Zero external dependencies, zero CPU overhead.
"""

import sys
import io
import wave
import struct
import math
import random
from typing import Optional

SAMPLE_RATE = 22050
DURATION = 8 # seconds loop buffer

def _generate_gamma_wav() -> bytes:
    """Generates an 8-second seamless loop of 40Hz Gamma wave with warm carrier tone."""
    total_samples = SAMPLE_RATE * DURATION
    carrier_freq = 200.0 # Warm, soothing G-note carrier
    mod_freq = 40.0     # 40Hz Gamma entrainment
    volume = 0.18        # Gentle volume

    raw_data = bytearray()
    for i in range(total_samples):
        t = i / SAMPLE_RATE
        carrier = math.sin(2 * math.pi * carrier_freq * t)
        # 40Hz envelope modulation
        envelope = 0.5 + 0.5 * math.sin(2 * math.pi * mod_freq * t)
        sample = int(carrier * envelope * volume * 32767)
        sample = max(-32768, min(32767, sample))
        raw_data.extend(struct.pack('<h', sample))

    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(raw_data)

    return wav_io.getvalue()

def _generate_brown_noise_wav() -> bytes:
    """Generates an 8-second seamless loop of deep Brown noise (rain/ocean surf acoustic curtain)."""
    total_samples = SAMPLE_RATE * DURATION
    volume = 0.15

    raw_data = bytearray()
    last_val = 0.0
    for _ in range(total_samples):
        white = random.uniform(-1.0, 1.0)
        # Brownian integration (random walk with leaky decay)
        brown = (last_val + (0.02 * white)) / 1.02
        last_val = brown
        # Soft clamp
        sample = int(brown * volume * 3.5 * 32767)
        sample = max(-32768, min(32767, sample))
        raw_data.extend(struct.pack('<h', sample))

    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(raw_data)

    return wav_io.getvalue()

class FocusAudioEngine:
    def __init__(self):
        self.mode = "OFF" # "OFF", "GAMMA", "BROWN"
        self._gamma_wav: Optional[bytes] = None
        self._brown_wav: Optional[bytes] = None

    def _ensure_buffers(self):
        if self._gamma_wav is None:
            self._gamma_wav = _generate_gamma_wav()
        if self._brown_wav is None:
            self._brown_wav = _generate_brown_noise_wav()

    def start_gamma(self):
        if sys.platform != "win32":
            return
        import winsound
        self._ensure_buffers()
        self.mode = "GAMMA"
        winsound.PlaySound(
            self._gamma_wav,
            winsound.SND_MEMORY | winsound.SND_ASYNC | winsound.SND_LOOP
        )

    def start_brown(self):
        if sys.platform != "win32":
            return
        import winsound
        self._ensure_buffers()
        self.mode = "BROWN"
        winsound.PlaySound(
            self._brown_wav,
            winsound.SND_MEMORY | winsound.SND_ASYNC | winsound.SND_LOOP
        )

    def stop(self):
        if sys.platform != "win32":
            return
        import winsound
        self.mode = "OFF"
        try:
            winsound.PlaySound(None, 0)
        except Exception:
            pass

    def toggle(self) -> str:
        """Cycles: OFF -> GAMMA 40Hz -> BROWN NOISE -> OFF."""
        if self.mode == "OFF":
            self.start_gamma()
        elif self.mode == "GAMMA":
            self.start_brown()
        else:
            self.stop()
        return self.mode

focus_audio = FocusAudioEngine()
