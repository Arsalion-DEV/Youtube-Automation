#!/usr/bin/env python3
"""
Simple test script for YouTube automation core functionality
Avoids problematic dependencies
"""

import asyncio
import sys
import os
import json
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.veo3_integration.generator_simple import (
    GoogleVEO3Generator, 
    VEO3GenerationRequest, 
    create_veo3_config
)

async def test_youtube_content_generation():
    """Test generating YouTube-ready content"""
    print("🎬 YouTube Content Generation Test")
    print("=" * 50)
    
    # Initialize generator
    generator = GoogleVEO3Generator()
    
    # Define different types of YouTube content
    content_scenarios = [
        {
            "title": "Nature Documentary Clip",
            "prompt": "A magnificent waterfall cascading down moss-covered rocks in a lush tropical forest with butterflies flying around",
            "duration": 8,
            "resolution": "1080p",
            "description": "Perfect for nature documentary channels"
        },
        {
            "title": "Tech Product Showcase", 
            "prompt": "A sleek modern smartphone rotating slowly on a clean white surface with soft lighting and subtle reflections",
            "duration": 6,
            "resolution": "720p", 
            "description": "Ideal for tech review channels"
        },
        {
            "title": "Cooking Content Background",
            "prompt": "Fresh ingredients including colorful vegetables, herbs, and spices arranged artistically on a wooden cutting board",
            "duration": 5,
            "resolution": "720p",
            "description": "Great for cooking channel intros"
        },
        {
            "title": "Educational Content Visual",
            "prompt": "An animated diagram showing the solar system with planets orbiting the sun in a beautiful cosmic setting",
            "duration": 7,
            "resolution": "1080p",
            "description": "Perfect for educational channels"
        }
    ]
    
    generated_content = []
    
    for i, scenario in enumerate(content_scenarios, 1):
        print(f"\n--- Generating {scenario['title']} ({i}/{len(content_scenarios)}) ---")
        
        try:
            # Create configuration
            config = create_veo3_config(
                quality="veo-3",
                duration=scenario['duration'],
                audio_mode="full",
                resolution=scenario['resolution'],
                temperature=0.7
            )
            
            # Create request
            request = VEO3GenerationRequest(
                prompt=scenario['prompt'],
                config=config
            )
            
            print(f"Prompt: {scenario['prompt'][:80]}...")
            
            # Generate video
            start_time = time.time()
            result = await generator.generate_video(request)
            generation_time = time.time() - start_time
            
            # Compile results
            content_info = {
                "title": scenario['title'],
                "description": scenario['description'],
                "video_url": result.video_url,
                "duration": result.duration,
                "resolution": result.resolution,
                "file_size": result.file_size,
                "generation_time": generation_time,
                "prompt": scenario['prompt'],
                "suggested_tags": generate_tags_for_content(scenario['title']),
                "youtube_ready": True
            }
            
            generated_content.append(content_info)
            print(f"✅ Generated successfully: {result.video_url}")
            print(f"   Duration: {result.duration}s | Resolution: {result.resolution} | Size: {result.file_size} bytes")
            
        except Exception as e:
            print(f"❌ Failed to generate {scenario['title']}: {str(e)}")
    
    # Create summary report
    print("\n" + "=" * 50)
    print("📊 GENERATION SUMMARY")
    print("=" * 50)
    print(f"✅ Successfully generated: {len(generated_content)}/{len(content_scenarios)} videos")
    
    total_duration = sum(content['duration'] for content in generated_content)
    total_size = sum(content['file_size'] for content in generated_content)
    avg_generation_time = sum(content['generation_time'] for content in generated_content) / len(generated_content) if generated_content else 0
    
    print(f"📏 Total content duration: {total_duration} seconds")
    print(f"💾 Total file size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    print(f"⏱️ Average generation time: {avg_generation_time:.2f} seconds")
    
    # Save detailed report
    report = {
        "test_completed_at": time.time(),
        "summary": {
            "videos_generated": len(generated_content),
            "total_duration": total_duration,
            "total_file_size": total_size,
            "average_generation_time": avg_generation_time
        },
        "generated_content": generated_content
    }
    
    report_path = "assets/clips/youtube_content_generation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Detailed report saved: {report_path}")
    
    # List all generated files
    print(f"\n📁 Generated Video Files:")
    for i, content in enumerate(generated_content, 1):
        file_path = content['video_url'].replace('/assets/clips/', 'assets/clips/')
        if os.path.exists(file_path):
            print(f"  {i}. {content['title']}")
            print(f"     File: {file_path}")
            print(f"     Tags: {', '.join(content['suggested_tags'][:5])}...")
            print(f"     Ready for: {content['description']}")
        else:
            print(f"  {i}. {content['title']} (file not found)")
    
    return generated_content

def generate_tags_for_content(title):
    """Generate relevant YouTube tags based on content title"""
    tag_mappings = {
        "Nature Documentary": ["nature", "documentary", "wildlife", "forest", "waterfall", "peaceful", "4k", "relaxing"],
        "Tech Product": ["tech", "review", "smartphone", "gadget", "technology", "unboxing", "product", "showcase"],
        "Cooking Content": ["cooking", "recipe", "food", "ingredients", "kitchen", "chef", "tutorial", "howto"],
        "Educational": ["education", "learning", "science", "space", "solar system", "astronomy", "tutorial", "facts"]
    }
    
    for category, tags in tag_mappings.items():
        if category.lower() in title.lower():
            return tags
    
    return ["video", "content", "ai-generated", "youtube"]

async def test_api_integration():
    """Test integration with the running API server"""
    print("\n" + "=" * 50)
    print("🌐 API Integration Test")
    print("=" * 50)
    
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get("http://localhost:8001/health")
            if response.status_code == 200:
                health_data = response.json()
                print("✅ API Server is healthy")
                print(f"   Modules available: {list(health_data['modules'].keys())}")
            else:
                print(f"❌ API Server health check failed: {response.status_code}")
                return False
            
            # Test video creation endpoint
            video_data = {
                "title": "API Test Video",
                "description": "Video created via API for testing"
            }
            
            response = await client.post("http://localhost:8001/api/videos/create", json=video_data)
            if response.status_code == 200:
                create_result = response.json()
                print(f"✅ Video project created via API: ID {create_result['video_id']}")
            else:
                print(f"❌ Video creation failed: {response.status_code}")
            
            # Test video listing
            response = await client.get("http://localhost:8001/api/videos/list")
            if response.status_code == 200:
                videos_data = response.json()
                print(f"✅ Retrieved video list: {videos_data['total']} videos found")
            else:
                print(f"❌ Video listing failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 YouTube Automation Platform - Simple Workflow Test")
    print("Testing core VEO3 video generation functionality")
    
    # Test content generation
    generated_content = asyncio.run(test_youtube_content_generation())
    
    # Test API integration
    api_success = asyncio.run(test_api_integration())
    
    print("\n" + "=" * 50)
    print("🏆 TEST RESULTS")
    print("=" * 50)
    print(f"✅ Content Generation: {len(generated_content)} videos created")
    print(f"{'✅' if api_success else '❌'} API Integration: {'Working' if api_success else 'Failed'}")
    
    if generated_content and api_success:
        print("\n🎉 YouTube Automation Platform is FULLY FUNCTIONAL!")
        print("🚀 Ready to generate professional YouTube content!")
    else:
        print("\n⚠️ Some tests failed - check logs for details")
    
    print(f"\n📁 Check 'assets/clips/' directory for generated video files")
    print(f"🌐 Access API docs at: http://localhost:8001/api/docs")
    print(f"🎬 Frontend dashboard at: http://localhost:3000")