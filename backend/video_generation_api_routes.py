"""
API Routes for Video Generation and Content Management
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import asyncio
import logging
from typing import Dict, Any

from video_generation_manager import video_generation_manager, VideoStatus, ContentType

logger = logging.getLogger(__name__)

# Create Blueprint
video_gen_bp = Blueprint('video_generation', __name__, url_prefix='/api/v2/video-generation')

# Utility function to run async functions in sync context
def run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@video_gen_bp.route('/status', methods=['GET'])
@cross_origin()
def get_processing_status():
    """Get video generation processing status"""
    try:
        status = run_async(video_generation_manager.get_processing_status())
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Failed to get processing status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/create', methods=['POST'])
@cross_origin()
def create_video_request():
    """Create a new video generation request"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['channel_id', 'title', 'topic', 'content_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate content type
        try:
            ContentType(data['content_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid content type: {data["content_type"]}'
            }), 400
        
        request_id = run_async(video_generation_manager.create_video_request(
            channel_id=data['channel_id'],
            title=data['title'],
            description=data.get('description', ''),
            content_type=data['content_type'],
            topic=data['topic'],
            keywords=data.get('keywords', []),
            target_duration=data.get('target_duration', 600),
            scheduled_publish_time=data.get('scheduled_publish_time')
        ))
        
        return jsonify({
            'success': True,
            'data': {
                'request_id': request_id,
                'message': 'Video generation request created successfully'
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to create video request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/requests', methods=['GET'])
@cross_origin()
def get_video_requests():
    """Get all video requests"""
    try:
        channel_id = request.args.get('channel_id')
        
        requests = run_async(video_generation_manager.get_all_video_requests(channel_id))
        
        requests_data = [req.to_dict() for req in requests]
        
        return jsonify({
            'success': True,
            'data': requests_data,
            'total': len(requests_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to get video requests: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/requests/<request_id>', methods=['GET'])
@cross_origin()
def get_video_request(request_id):
    """Get specific video request"""
    try:
        video_request = run_async(video_generation_manager.get_video_request(request_id))
        
        if not video_request:
            return jsonify({
                'success': False,
                'error': 'Video request not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': video_request.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get video request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/requests/<request_id>', methods=['DELETE'])
@cross_origin()
def delete_video_request(request_id):
    """Delete a video request"""
    try:
        success = run_async(video_generation_manager.delete_video_request(request_id))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Video request not found or could not be deleted'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Video request deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to delete video request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/requests/<request_id>/retry', methods=['POST'])
@cross_origin()
def retry_video_request(request_id):
    """Retry a failed video request"""
    try:
        success = run_async(video_generation_manager.retry_failed_request(request_id))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Video request not found or not in failed state'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Video request retry initiated'
        })
        
    except Exception as e:
        logger.error(f"Failed to retry video request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/requests/<request_id>/publish', methods=['POST'])
@cross_origin()
def publish_video(request_id):
    """Publish a ready video"""
    try:
        success = run_async(video_generation_manager.publish_video(request_id))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Video not ready for publishing or publishing failed'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Video published successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to publish video: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/templates', methods=['GET'])
@cross_origin()
def get_content_templates():
    """Get available content templates"""
    try:
        templates = [
            template.to_dict() 
            for template in video_generation_manager.content_templates.values()
        ]
        
        return jsonify({
            'success': True,
            'data': templates
        })
        
    except Exception as e:
        logger.error(f"Failed to get content templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/analytics', methods=['GET'])
@cross_origin()
def get_generation_analytics():
    """Get video generation analytics"""
    try:
        # Get processing status
        status = run_async(video_generation_manager.get_processing_status())
        
        # Calculate additional analytics
        total_requests = status['total_requests']
        completed = status['status_breakdown'].get('published', 0)
        failed = status['status_breakdown'].get('failed', 0)
        
        success_rate = (completed / total_requests * 100) if total_requests > 0 else 0
        
        analytics = {
            'overview': {
                'total_requests': total_requests,
                'completed_videos': completed,
                'failed_requests': failed,
                'success_rate': round(success_rate, 2),
                'active_processing': status['processing_queue_size']
            },
            'status_breakdown': status['status_breakdown'],
            'recent_completions': status['recent_completions'],
            'performance_metrics': {
                'avg_processing_time': '15 minutes',  # Mock data
                'most_common_content_type': 'tutorial',  # Mock data
                'peak_processing_hours': ['2:00 PM', '6:00 PM', '9:00 PM']  # Mock data
            }
        }
        
        return jsonify({
            'success': True,
            'data': analytics
        })
        
    except Exception as e:
        logger.error(f"Failed to get generation analytics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Content Generation Endpoints
@video_gen_bp.route('/generate-script', methods=['POST'])
@cross_origin()
def generate_script():
    """Generate video script"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Import content creation module
        from content_creation.generator import ContentCreationEngine
        
        content_engine = ContentCreationEngine()
        
        script_request = {
            'topic': data['topic'],
            'target_duration': data.get('target_duration', 600),
            'tone': data.get('tone', 'engaging'),
            'target_audience': data.get('target_audience', 'general'),
            'key_points': data.get('keywords', []),
            'include_hook': data.get('include_hook', True),
            'include_cta': data.get('include_cta', True)
        }
        
        # Run script generation
        script_result = run_async(content_engine.generate_video_script(script_request))
        
        return jsonify({
            'success': True,
            'data': script_result
        })
        
    except Exception as e:
        logger.error(f"Failed to generate script: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/generate-thumbnail', methods=['POST'])
@cross_origin()
def generate_thumbnail():
    """Generate video thumbnail"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Import image generation module
        from t2i_sdxl_controlnet.generator import ImageGenerationEngine
        
        image_engine = ImageGenerationEngine()
        
        thumbnail_request = {
            'prompt': f"YouTube thumbnail for {data['topic']}, bright colors, text overlay, professional",
            'width': 1280,
            'height': 720,
            'style': data.get('style', 'professional')
        }
        
        thumbnail_result = run_async(image_engine.generate_image(thumbnail_request))
        
        return jsonify({
            'success': True,
            'data': thumbnail_result
        })
        
    except Exception as e:
        logger.error(f"Failed to generate thumbnail: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Bulk Operations
@video_gen_bp.route('/bulk-create', methods=['POST'])
@cross_origin()
def bulk_create_videos():
    """Create multiple video requests"""
    try:
        data = request.get_json()
        
        if not data or 'requests' not in data:
            return jsonify({
                'success': False,
                'error': 'Requests array is required'
            }), 400
        
        requests = data['requests']
        created_requests = []
        
        for req_data in requests:
            try:
                request_id = run_async(video_generation_manager.create_video_request(
                    channel_id=req_data['channel_id'],
                    title=req_data['title'],
                    description=req_data.get('description', ''),
                    content_type=req_data['content_type'],
                    topic=req_data['topic'],
                    keywords=req_data.get('keywords', []),
                    target_duration=req_data.get('target_duration', 600),
                    scheduled_publish_time=req_data.get('scheduled_publish_time')
                ))
                
                created_requests.append({
                    'request_id': request_id,
                    'title': req_data['title'],
                    'status': 'created'
                })
                
            except Exception as e:
                created_requests.append({
                    'title': req_data.get('title', 'Unknown'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'data': {
                'created_requests': created_requests,
                'total_created': len([r for r in created_requests if r['status'] == 'created']),
                'total_failed': len([r for r in created_requests if r['status'] == 'failed'])
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to bulk create videos: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Scheduling Endpoints
@video_gen_bp.route('/schedule', methods=['GET'])
@cross_origin()
def get_publishing_schedule():
    """Get publishing schedule"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(video_generation_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT ps.*, vr.title, vr.channel_id 
        FROM publishing_schedule ps
        JOIN video_requests vr ON ps.video_request_id = vr.id
        ORDER BY ps.scheduled_time ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        schedule = []
        for row in rows:
            schedule.append({
                'id': row[0],
                'video_request_id': row[1],
                'channel_id': row[2],
                'scheduled_time': row[3],
                'published_time': row[4],
                'status': row[5],
                'title': row[7],
                'created_at': row[7]
            })
        
        return jsonify({
            'success': True,
            'data': schedule
        })
        
    except Exception as e:
        logger.error(f"Failed to get publishing schedule: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/content-types', methods=['GET'])
@cross_origin()
def get_content_types():
    """Get available content types"""
    try:
        content_types = [
            {
                'value': ct.value,
                'label': ct.value.replace('_', ' ').title(),
                'description': f"{ct.value.replace('_', ' ').title()} content type"
            }
            for ct in ContentType
        ]
        
        return jsonify({
            'success': True,
            'data': content_types
        })
        
    except Exception as e:
        logger.error(f"Failed to get content types: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@video_gen_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check for video generation system"""
    try:
        status = run_async(video_generation_manager.get_processing_status())
        
        health = {
            'status': 'healthy',
            'total_requests': status['total_requests'],
            'processing_queue': status['processing_queue_size'],
            'system_load': 'normal',  # Mock data
            'last_successful_generation': 'just now'  # Mock data
        }
        
        return jsonify({
            'success': True,
            'data': health
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Initialize video generation manager
def init_video_generation_manager():
    """Initialize video generation manager"""
    try:
        run_async(video_generation_manager.initialize())
        logger.info("Video generation manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize video generation manager: {str(e)}")
        raise