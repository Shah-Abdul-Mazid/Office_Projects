import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from app.services.tts import synthesize_voice
from app.schemas import Voice

async def main():
    print("Testing Edge TTS integration...")
    try:
        # Test guide voice
        result_guide = await synthesize_voice(
            "Hello, I am your guide for this meditation.",
            Voice.guide
        )
        print(f"Guide audio generated: {result_guide.path}")
        
        # Test student voice
        result_student = await synthesize_voice(
            "I am ready to begin my journey.",
            Voice.student
        )
        print(f"Student audio generated: {result_student.path}")
        
        print("Success! Both voices generated correctly.")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
