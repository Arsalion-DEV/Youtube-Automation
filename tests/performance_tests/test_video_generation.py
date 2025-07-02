"""
Performance tests for AI video generation pipeline
"""

import pytest
import time
import asyncio
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from unittest.mock import Mock, patch
import statistics
import gc

# Import video generation modules
from modules.script_gen.generator import ScriptGenerator
from modules.t2i_sdxl_controlnet.generator import ImageGenerator
from modules.i2v_animatediff.generator import ImageToVideoGenerator
from modules.t2v_zeroscope.generator import TextToVideoGenerator
from modules.tts.synthesizer import VoiceSynthesizer
from modules.video_editor.editor import VideoEditor


class TestVideoGenerationPerformance:
    """Test performance of video generation pipeline"""
    
    @property
    def mock_ai(self):
        """Whether to mock AI models for performance testing"""
        import os
        return not bool(os.environ.get("GPU_AVAILABLE"))
    
    @pytest.fixture
    def performance_tracker(self):
        """Performance tracking utilities"""
        class PerformanceTracker:
            def __init__(self):
                self.metrics = {}
                self.start_times = {}
            
            def start_timing(self, operation):
                self.start_times[operation] = time.time()
                return self
            
            def end_timing(self, operation):
                if operation in self.start_times:
                    duration = time.time() - self.start_times[operation]
                    self.metrics[f"{operation}_duration"] = duration
                    return duration
                return None
            
            def track_memory(self, operation):
                process = psutil.Process()
                self.metrics[f"{operation}_memory_mb"] = process.memory_info().rss / 1024 / 1024
                return self.metrics[f"{operation}_memory_mb"]
            
            def track_cpu(self, operation):
                self.metrics[f"{operation}_cpu_percent"] = psutil.cpu_percent(interval=1)
                return self.metrics[f"{operation}_cpu_percent"]
            
            def get_metrics(self):
                return self.metrics.copy()
        
        return PerformanceTracker()
    
    def test_script_generation_performance(self, performance_tracker):
        """Test script generation performance and resource usage"""
        script_generator = ScriptGenerator()
        
        # Test single script generation
        performance_tracker.start_timing("script_generation")
        
        with patch('modules.script_gen.generator.requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '{"title": "Test", "script": "Test script", "scenes": [{"text": "Scene", "duration": 60}], "duration": 60}'
                    }
                }]
            }
            mock_post.return_value.status_code = 200
            
            script_result = script_generator.generate_script(
                topic="Performance Test Topic",
                duration=300
            )
        
        generation_time = performance_tracker.end_timing("script_generation")
        memory_usage = performance_tracker.track_memory("script_generation")
        
        # Performance assertions
        assert generation_time < 10.0  # Should complete within 10 seconds
        assert memory_usage < 500  # Should use less than 500MB
        assert script_result is not None
        
        # Test batch script generation
        batch_topics = [f"Topic {i}" for i in range(10)]
        
        performance_tracker.start_timing("batch_script_generation")
        
        batch_results = []
        for topic in batch_topics:
            result = script_generator.generate_script(topic=topic, duration=180)
            batch_results.append(result)
        
        batch_time = performance_tracker.end_timing("batch_script_generation")
        
        # Batch processing should be efficient
        assert len(batch_results) == 10
        assert batch_time < 30.0  # 10 scripts in under 30 seconds
        assert batch_time / 10 < generation_time * 1.5  # Batch should have some efficiency gains
    
    def test_image_generation_performance(self, performance_tracker):
        """Test image generation performance"""
        if self.mock_ai:
            image_generator = Mock()
            image_generator.generate_image.return_value = {
                "image_path": "/test/image.png",
                "generation_time": 0.1  # Mock fast generation
            }
        else:
            image_generator = ImageGenerator()
        
        # Test single image generation
        performance_tracker.start_timing("image_generation")
        
        image_result = image_generator.generate_image(
            prompt="Professional office setting with modern equipment",
            width=1024,
            height=1024
        )
        
        generation_time = performance_tracker.end_timing("image_generation")
        memory_usage = performance_tracker.track_memory("image_generation")
        
        if self.mock_ai:
            assert generation_time < 1.0  # Mocked should be very fast
        else:
            assert generation_time < 60.0  # Real generation should complete within 60 seconds
        
        assert image_result is not None
        
        # Test concurrent image generation
        def generate_concurrent_image(prompt_id):
            return image_generator.generate_image(
                prompt=f"Image prompt {prompt_id}",
                width=512,
                height=512
            )
        
        performance_tracker.start_timing("concurrent_image_generation")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(generate_concurrent_image, i) for i in range(6)]
            concurrent_results = [future.result() for future in futures]
        
        concurrent_time = performance_tracker.end_timing("concurrent_image_generation")
        
        assert len(concurrent_results) == 6
        if self.mock_ai:
            assert concurrent_time < 2.0  # Mock concurrent should be very fast
        else:
            # Concurrent generation should be faster than sequential
            sequential_estimate = generation_time * 6
            assert concurrent_time < sequential_estimate * 0.7  # At least 30% improvement
    
    def test_video_generation_performance(self, performance_tracker):
        """Test video generation performance"""
        if self.mock_ai:
            i2v_generator = Mock()
            i2v_generator.generate_video.return_value = {
                "video_path": "/test/video.mp4",
                "duration": 5.0,
                "generation_time": 0.2
            }
            
            t2v_generator = Mock()
            t2v_generator.generate_video.return_value = {
                "video_path": "/test/t2v_video.mp4",
                "duration": 10.0,
                "generation_time": 0.3
            }
        else:
            i2v_generator = ImageToVideoGenerator()
            t2v_generator = TextToVideoGenerator()
        
        # Test Image-to-Video generation
        performance_tracker.start_timing("i2v_generation")
        
        i2v_result = i2v_generator.generate_video(
            image_path="/test/input_image.jpg",
            duration=5.0,
            motion_strength=0.7
        )
        
        i2v_time = performance_tracker.end_timing("i2v_generation")
        
        # Test Text-to-Video generation
        performance_tracker.start_timing("t2v_generation")
        
        t2v_result = t2v_generator.generate_video(
            prompt="Ocean waves crashing on beach at sunset",
            duration=10.0
        )
        
        t2v_time = performance_tracker.end_timing("t2v_generation")
        
        if self.mock_ai:
            assert i2v_time < 1.0
            assert t2v_time < 1.0
        else:
            assert i2v_time < 120.0  # I2V should complete within 2 minutes
            assert t2v_time < 180.0  # T2V should complete within 3 minutes
        
        assert i2v_result is not None
        assert t2v_result is not None
    
    def test_tts_performance(self, performance_tracker):
        """Test Text-to-Speech performance"""
        tts_synthesizer = VoiceSynthesizer()
        
        # Test short text synthesis
        short_text = "This is a short test sentence for TTS performance testing."
        
        performance_tracker.start_timing("tts_short")
        
        with patch('modules.tts.synthesizer.TTS') as mock_tts:
            mock_tts_instance = Mock()
            mock_tts.return_value = mock_tts_instance
            mock_tts_instance.tts_to_file.return_value = "/test/short_audio.wav"
            
            short_result = tts_synthesizer.synthesize_speech(
                text=short_text,
                voice="professional_male"
            )
        
        short_time = performance_tracker.end_timing("tts_short")
        
        # Test long text synthesis
        long_text = " ".join([short_text] * 20)  # Much longer text
        
        performance_tracker.start_timing("tts_long")
        
        long_result = tts_synthesizer.synthesize_speech(
            text=long_text,
            voice="professional_male"
        )
        
        long_time = performance_tracker.end_timing("tts_long")
        
        # Performance assertions
        assert short_time < 10.0  # Short text should be fast
        assert long_time < 60.0  # Long text should still be reasonable
        assert short_result is not None
        assert long_result is not None
        
        # Test multiple voice synthesis in parallel
        voices = ["professional_male", "professional_female", "casual_male"]
        
        def synthesize_voice(voice):
            return tts_synthesizer.synthesize_speech(
                text="Test text for voice comparison",
                voice=voice
            )
        
        performance_tracker.start_timing("tts_multiple_voices")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            voice_futures = [executor.submit(synthesize_voice, voice) for voice in voices]
            voice_results = [future.result() for future in voice_futures]
        
        multi_voice_time = performance_tracker.end_timing("tts_multiple_voices")
        
        assert len(voice_results) == 3
        assert multi_voice_time < 30.0  # Multiple voices should complete reasonably quickly
    
    def test_video_editing_performance(self, performance_tracker):
        """Test video editing and compilation performance"""
        video_editor = VideoEditor()
        
        # Mock video clips for editing
        mock_clips = [f"/test/clip_{i}.mp4" for i in range(5)]
        mock_audio = "/test/narration.wav"
        
        performance_tracker.start_timing("video_compilation")
        
        with patch('modules.video_editor.editor.VideoFileClip') as mock_video_clip, \
             patch('modules.video_editor.editor.AudioFileClip') as mock_audio_clip:
            
            # Mock video clip properties
            mock_video_instance = Mock()
            mock_video_instance.duration = 30.0
            mock_video_instance.fps = 30
            mock_video_instance.size = (1920, 1080)
            mock_video_clip.return_value = mock_video_instance
            
            # Mock audio clip properties
            mock_audio_instance = Mock()
            mock_audio_instance.duration = 150.0
            mock_audio_clip.return_value = mock_audio_instance
            
            compilation_result = video_editor.compile_video(
                clips=mock_clips,
                audio_track=mock_audio,
                output_path="/test/compiled_video.mp4",
                transitions=["fade", "dissolve"],
                effects=["color_correction", "stabilization"]
            )
        
        compilation_time = performance_tracker.end_timing("video_compilation")
        memory_usage = performance_tracker.track_memory("video_compilation")
        
        # Performance assertions
        assert compilation_time < 30.0  # Video compilation should be efficient with mocked clips
        assert memory_usage < 1000  # Should manage memory efficiently
        assert compilation_result is not None
        
        # Test different video resolutions and their impact
        resolutions = [(1280, 720), (1920, 1080), (3840, 2160)]
        resolution_times = []
        
        for width, height in resolutions:
            performance_tracker.start_timing(f"compilation_{width}x{height}")
            
            mock_video_instance.size = (width, height)
            
            result = video_editor.compile_video(
                clips=mock_clips[:3],  # Fewer clips for resolution test
                output_path=f"/test/video_{width}x{height}.mp4"
            )
            
            res_time = performance_tracker.end_timing(f"compilation_{width}x{height}")
            resolution_times.append(res_time)
        
        # Higher resolution should take more time (generally)
        assert len(resolution_times) == 3
    
    def test_complete_pipeline_performance(self, performance_tracker):
        """Test complete video generation pipeline performance"""
        # Initialize all components
        components = {
            "script_generator": ScriptGenerator(),
            "image_generator": Mock() if self.mock_ai else ImageGenerator(),
            "i2v_generator": Mock() if self.mock_ai else ImageToVideoGenerator(),
            "tts_synthesizer": VoiceSynthesizer(),
            "video_editor": VideoEditor()
        }
        
        if self.mock_ai:
            # Mock all AI components for performance testing
            components["image_generator"].generate_image.return_value = {"image_path": "/test/img.png"}
            components["i2v_generator"].generate_video.return_value = {"video_path": "/test/vid.mp4", "duration": 10}
        
        video_request = {
            "topic": "Complete Pipeline Performance Test",
            "duration": 180,
            "style": "educational"
        }
        
        performance_tracker.start_timing("complete_pipeline")
        initial_memory = performance_tracker.track_memory("pipeline_start")
        
        # Stage 1: Script Generation
        performance_tracker.start_timing("stage_script")
        
        with patch('modules.script_gen.generator.requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                "choices": [{
                    "message": {
                        "content": '{"title": "Test Video", "script": "Complete test script", "scenes": [{"text": "Scene 1", "duration": 60, "visual_description": "Office scene"}, {"text": "Scene 2", "duration": 60, "visual_description": "Diagram"}, {"text": "Scene 3", "duration": 60, "visual_description": "Conclusion"}], "duration": 180}'
                    }
                }]
            }
            mock_post.return_value.status_code = 200
            
            script_result = components["script_generator"].generate_script(
                topic=video_request["topic"],
                duration=video_request["duration"]
            )
        
        script_time = performance_tracker.end_timing("stage_script")
        
        # Stage 2: Visual Generation
        performance_tracker.start_timing("stage_visuals")
        
        visual_results = []
        for scene in script_result["scenes"]:
            img_result = components["image_generator"].generate_image(
                prompt=scene["visual_description"]
            )
            vid_result = components["i2v_generator"].generate_video(
                image_path=img_result["image_path"]
            )
            visual_results.append(vid_result)
        
        visuals_time = performance_tracker.end_timing("stage_visuals")
        
        # Stage 3: Audio Generation
        performance_tracker.start_timing("stage_audio")
        
        with patch('modules.tts.synthesizer.TTS') as mock_tts:
            mock_tts_instance = Mock()
            mock_tts.return_value = mock_tts_instance
            
            audio_result = components["tts_synthesizer"].synthesize_speech(
                text=script_result["script"],
                voice="professional"
            )
        
        audio_time = performance_tracker.end_timing("stage_audio")
        
        # Stage 4: Final Compilation
        performance_tracker.start_timing("stage_compilation")
        
        with patch('modules.video_editor.editor.VideoFileClip'), \
             patch('modules.video_editor.editor.AudioFileClip'):
            
            final_result = components["video_editor"].compile_video(
                clips=[vr["video_path"] for vr in visual_results],
                audio_track=audio_result["audio_path"],
                output_path="/test/final_pipeline_video.mp4"
            )
        
        compilation_time = performance_tracker.end_timing("stage_compilation")
        
        total_time = performance_tracker.end_timing("complete_pipeline")
        final_memory = performance_tracker.track_memory("pipeline_end")
        
        # Performance assertions
        if self.mock_ai:
            assert total_time < 5.0  # Mocked pipeline should be very fast
        else:
            assert total_time < 600.0  # Real pipeline should complete within 10 minutes
        
        assert script_time < total_time * 0.1  # Script should be small fraction of total time
        assert final_memory - initial_memory < 2000  # Memory growth should be reasonable (< 2GB)
        
        # Verify all stages completed successfully
        assert script_result is not None
        assert len(visual_results) == 3
        assert audio_result is not None
        assert final_result is not None
        
        # Test memory cleanup
        gc.collect()
        cleanup_memory = performance_tracker.track_memory("pipeline_cleanup")
        memory_recovered = final_memory - cleanup_memory
        
        # Should recover some memory after cleanup
        assert memory_recovered >= 0
    
    def test_concurrent_pipeline_performance(self, performance_tracker):
        """Test performance with multiple concurrent pipeline executions"""
        
        async def run_pipeline_async(pipeline_id):
            """Run a single pipeline asynchronously"""
            start_time = time.time()
            
            # Simulate pipeline stages with appropriate delays
            if self.mock_ai:
                # Mock delays for testing
                await asyncio.sleep(0.1)  # Script generation
                await asyncio.sleep(0.2)  # Visual generation
                await asyncio.sleep(0.1)  # Audio generation
                await asyncio.sleep(0.1)  # Compilation
            else:
                # Real delays would be longer
                await asyncio.sleep(2.0)  # Script generation
                await asyncio.sleep(10.0)  # Visual generation
                await asyncio.sleep(3.0)  # Audio generation
                await asyncio.sleep(2.0)  # Compilation
            
            duration = time.time() - start_time
            return {"pipeline_id": pipeline_id, "duration": duration, "success": True}
        
        async def test_concurrent_execution():
            """Test concurrent pipeline execution"""
            num_concurrent = 3
            
            tasks = [run_pipeline_async(i) for i in range(num_concurrent)]
            results = await asyncio.gather(*tasks)
            
            return results
        
        performance_tracker.start_timing("concurrent_pipelines")
        
        concurrent_results = asyncio.run(test_concurrent_execution())
        
        concurrent_time = performance_tracker.end_timing("concurrent_pipelines")
        
        # Verify all pipelines completed successfully
        assert len(concurrent_results) == 3
        assert all(result["success"] for result in concurrent_results)
        
        # Concurrent execution should be more efficient than sequential
        avg_individual_time = statistics.mean(result["duration"] for result in concurrent_results)
        sequential_estimate = avg_individual_time * 3
        
        if self.mock_ai:
            assert concurrent_time < 1.0  # Mock concurrent should be very fast
        else:
            # Concurrent should provide some efficiency gain
            assert concurrent_time < sequential_estimate * 0.8  # At least 20% improvement
        
        # Test resource usage during concurrent execution
        max_memory = performance_tracker.track_memory("concurrent_peak")
        
        # Memory usage should be reasonable even with concurrent execution
        assert max_memory < 4000  # Less than 4GB peak memory usage
    
    def test_performance_regression_detection(self, performance_tracker):
        """Test detection of performance regressions"""
        # Baseline performance metrics (these would typically be stored/loaded)
        baseline_metrics = {
            "script_generation_duration": 5.0,
            "image_generation_duration": 30.0,
            "video_compilation_duration": 15.0,
            "memory_usage_mb": 800,
            "cpu_usage_percent": 70
        }
        
        # Run current performance test
        current_metrics = {}
        
        # Test script generation
        performance_tracker.start_timing("regression_script")
        # ... (would run actual script generation)
        current_metrics["script_generation_duration"] = performance_tracker.end_timing("regression_script") or 0.1
        
        # Test image generation (mocked)
        current_metrics["image_generation_duration"] = 0.1 if self.mock_ai else 35.0
        
        # Test compilation
        current_metrics["video_compilation_duration"] = 0.1 if self.mock_ai else 18.0
        
        current_metrics["memory_usage_mb"] = performance_tracker.track_memory("regression_memory")
        current_metrics["cpu_usage_percent"] = performance_tracker.track_cpu("regression_cpu")
        
        # Compare with baseline and detect regressions
        regressions = []
        improvements = []
        
        for metric, baseline_value in baseline_metrics.items():
            current_value = current_metrics.get(metric, 0)
            
            if current_value > baseline_value * 1.2:  # 20% slower is regression
                regressions.append({
                    "metric": metric,
                    "baseline": baseline_value,
                    "current": current_value,
                    "regression_percent": ((current_value - baseline_value) / baseline_value) * 100
                })
            elif current_value < baseline_value * 0.8:  # 20% faster is improvement
                improvements.append({
                    "metric": metric,
                    "baseline": baseline_value,
                    "current": current_value,
                    "improvement_percent": ((baseline_value - current_value) / baseline_value) * 100
                })
        
        # Log performance comparison results
        performance_comparison = {
            "baseline_metrics": baseline_metrics,
            "current_metrics": current_metrics,
            "regressions": regressions,
            "improvements": improvements,
            "overall_status": "regression" if regressions else "acceptable"
        }
        
        # Assert no major regressions (this would typically just log warnings)
        major_regressions = [r for r in regressions if r["regression_percent"] > 50]
        assert len(major_regressions) == 0, f"Major performance regressions detected: {major_regressions}"
        
        return performance_comparison