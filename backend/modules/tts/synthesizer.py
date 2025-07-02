"""
Text-to-Speech Synthesizer Module
Handles voice synthesis for YouTube automation
"""

import os
import logging
import asyncio
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class TTSProvider(Enum):
    """TTS Provider options"""
    OPENAI = "openai"
    ELEVENLABS = "elevenlabs"
    GOOGLE = "google"
    SYSTEM = "system"

class TTSVoice(Enum):
    """Available TTS voices"""
    MALE_PROFESSIONAL = "male_professional"
    FEMALE_PROFESSIONAL = "female_professional"
    MALE_CASUAL = "male_casual"
    FEMALE_CASUAL = "female_casual"
    NARRATOR = "narrator"

class TTSSynthesizer:
    """Text-to-Speech Synthesizer"""
    
    def __init__(self):
        self.provider = TTSProvider.SYSTEM  # Default to system TTS
        self.voice = TTSVoice.MALE_PROFESSIONAL
        self.output_dir = Path("assets/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # API configurations
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        
        logger.info("TTS Synthesizer initialized")
    
    async def synthesize(
        self, 
        text: str, 
        voice: Optional[TTSVoice] = None,
        provider: Optional[TTSProvider] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Synthesize text to speech"""
        try:
            # Use provided parameters or defaults
            voice = voice or self.voice
            provider = provider or self.provider
            
            if not output_path:
                import time
                filename = f"tts_{int(time.time())}.wav"
                output_path = str(self.output_dir / filename)
            
            logger.info(f"Synthesizing text with {provider.value} voice {voice.value}")
            
            # Choose synthesis method based on provider
            if provider == TTSProvider.OPENAI:
                await self._synthesize_openai(text, voice, output_path)
            elif provider == TTSProvider.ELEVENLABS:
                await self._synthesize_elevenlabs(text, voice, output_path)
            elif provider == TTSProvider.GOOGLE:
                await self._synthesize_google(text, voice, output_path)
            else:
                await self._synthesize_system(text, voice, output_path)
            
            logger.info(f"TTS synthesis completed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {str(e)}")
            raise
    
    async def _synthesize_openai(self, text: str, voice: TTSVoice, output_path: str):
        """Synthesize using OpenAI TTS"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Mock implementation - would use actual OpenAI TTS API
        await self._create_mock_audio(text, output_path)
        logger.info("Mock OpenAI TTS synthesis completed")
    
    async def _synthesize_elevenlabs(self, text: str, voice: TTSVoice, output_path: str):
        """Synthesize using ElevenLabs TTS"""
        if not self.elevenlabs_api_key:
            raise ValueError("ElevenLabs API key not configured")
        
        # Mock implementation - would use actual ElevenLabs API
        await self._create_mock_audio(text, output_path)
        logger.info("Mock ElevenLabs TTS synthesis completed")
    
    async def _synthesize_google(self, text: str, voice: TTSVoice, output_path: str):
        """Synthesize using Google Cloud TTS"""
        # Mock implementation - would use Google Cloud TTS
        await self._create_mock_audio(text, output_path)
        logger.info("Mock Google TTS synthesis completed")
    
    async def _synthesize_system(self, text: str, voice: TTSVoice, output_path: str):
        """Synthesize using system TTS (espeak/pico2wave)"""
        try:
            # Try to use system TTS tools
            import subprocess
            
            # Try espeak first
            result = subprocess.run([
                'espeak', '-s', '150', '-v', 'en+m3', '-w', output_path, text
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("System TTS (espeak) synthesis completed")
                return
            
            # Fall back to mock audio
            await self._create_mock_audio(text, output_path)
            
        except FileNotFoundError:
            # espeak not available, create mock audio
            await self._create_mock_audio(text, output_path)
            logger.info("System TTS not available, created mock audio")
    
    async def _create_mock_audio(self, text: str, output_path: str):
        """Create mock audio file for testing"""
        # Create a simple sine wave audio file using numpy/scipy if available
        try:
            import numpy as np
            import wave
            
            # Generate a simple sine wave
            duration = len(text) * 0.1  # 0.1 seconds per character
            sample_rate = 44100
            frequency = 440  # A4 note
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
            
            # Convert to 16-bit integers
            audio_data = (audio_data * 32767).astype(np.int16)
            
            # Write WAV file
            with wave.open(output_path, 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            logger.info("Mock audio file created with sine wave")
            
        except ImportError:
            # NumPy not available, create empty audio file
            with open(output_path, 'wb') as f:
                # Write minimal WAV header for empty audio
                wav_header = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
                f.write(wav_header)
            
            logger.info("Mock audio file created (empty)")
    
    def get_available_voices(self, provider: Optional[TTSProvider] = None) -> List[TTSVoice]:
        """Get available voices for a provider"""
        # For now, return all voices regardless of provider
        return list(TTSVoice)
    
    def estimate_duration(self, text: str) -> float:
        """Estimate audio duration based on text length"""
        # Rough estimate: 150 words per minute, 5 characters per word
        words = len(text) / 5
        minutes = words / 150
        return minutes * 60  # Return seconds
    
    def set_provider(self, provider: TTSProvider):
        """Set the TTS provider"""
        self.provider = provider
        logger.info(f"TTS provider set to: {provider.value}")
    
    def set_voice(self, voice: TTSVoice):
        """Set the default voice"""
        self.voice = voice
        logger.info(f"TTS voice set to: {voice.value}")

# Utility functions
def create_tts_request(
    text: str,
    voice: str = "male_professional",
    provider: str = "system",
    speed: float = 1.0,
    pitch: float = 1.0
) -> Dict[str, Any]:
    """Create TTS request parameters"""
    return {
        "text": text,
        "voice": TTSVoice(voice),
        "provider": TTSProvider(provider),
        "speed": max(0.5, min(2.0, speed)),
        "pitch": max(0.5, min(2.0, pitch))
    }