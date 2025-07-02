#!/usr/bin/env python3
"""
Test script for VEO3 video generation
"""

import asyncio
import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.veo3_integration.generator_simple import (
    GoogleVEO3Generator, 
    VEO3GenerationRequest, 
    create_veo3_config
)

async def test_veo3_generation():
    """Test VEO3 video generation"""
    print("Testing VEO3 Video Generation...")
    
    # Initialize the generator
    generator = GoogleVEO3Generator()
    
    # Create configuration
    config = create_veo3_config(
        quality="veo-3",
        duration=5,
        audio_mode="full",
        resolution="720p",
        temperature=0.7
    )
    
    # Create generation request
    request = VEO3GenerationRequest(
        prompt="A beautiful ocean wave crashing on a sandy beach at sunset with golden reflections on the water",
        config=config
    )
    
    print(f"Generating video with prompt: {request.prompt}")
    print(f"Configuration: {config}")
    
    try:
        # Generate the video
        result = await generator.generate_video(request)
        
        print("\n✅ Video Generation Successful!")
        print(f"Video URL: {result.video_url}")
        print(f"Duration: {result.duration} seconds")
        print(f"Resolution: {result.resolution}")
        print(f"File Size: {result.file_size} bytes")
        print(f"Generation Time: {result.generation_time:.2f} seconds")
        print(f"Metadata: {json.dumps(result.metadata, indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Video Generation Failed: {str(e)}")
        return None

async def test_multiple_videos():
    """Test generating multiple videos with different prompts"""
    prompts = [
        "A futuristic city skyline with flying cars and neon lights at night",
        "A peaceful forest with sunlight filtering through the trees and birds flying",
        "A space station orbiting Earth with astronauts working outside in zero gravity"
    ]
    
    generator = GoogleVEO3Generator()
    results = []
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- Generating Video {i}/3 ---")
        
        config = create_veo3_config(
            quality="veo-3",
            duration=6,
            resolution="720p"
        )
        
        request = VEO3GenerationRequest(prompt=prompt, config=config)
        
        try:
            result = await generator.generate_video(request)
            results.append(result)
            print(f"✅ Video {i} generated: {result.video_url}")
        except Exception as e:
            print(f"❌ Video {i} failed: {str(e)}")
    
    return results

if __name__ == "__main__":
    print("🎬 VEO3 Video Generation Test")
    print("=" * 50)
    
    # Test single video generation
    result = asyncio.run(test_veo3_generation())
    
    if result:
        print("\n" + "=" * 50)
        print("🎯 Testing Multiple Video Generation")
        
        # Test multiple video generation
        results = asyncio.run(test_multiple_videos())
        
        print(f"\n📊 Summary: Generated {len(results)} videos successfully")
        
        # List all generated video files
        print("\n📁 Generated Video Files:")
        import glob
        video_files = glob.glob("assets/clips/*.mp4")
        for i, file_path in enumerate(video_files, 1):
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            print(f"  {i}. {file_path} ({file_size} bytes)")
    
    print("\n🏁 Test completed!")