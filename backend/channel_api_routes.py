"""
API Routes for Multi-Channel Management System
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from channel_manager import (
    channel_manager, 
    ChannelStatus, 
    APIProviderType,
    VidIQIntegration,
    SocialBladeIntegration,
    TubeBuddyIntegration
)

logger = logging.getLogger(__name__)

# Create Blueprint
channel_bp = Blueprint('channels', __name__, url_prefix='/api/v2/channels')

# Utility function to run async functions in sync context
def run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@channel_bp.route('/system/status', methods=['GET'])
@cross_origin()
def get_system_status():
    """Get overall system status"""
    try:
        status = run_async(channel_manager.get_system_status())
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/', methods=['GET'])
@cross_origin()
def get_all_channels():
    """Get all channels"""
    try:
        channels = run_async(channel_manager.get_all_channels())
        channels_data = [
            {
                'channel_id': ch.channel_id,
                'channel_name': ch.channel_name,
                'gmail_account': ch.gmail_account,
                'status': ch.status.value,
                'api_configurations': {
                    provider: {
                        'provider': config.provider.value,
                        'monthly_limit': config.monthly_limit,
                        'current_usage': config.current_usage,
                        'is_active': config.is_active,
                        'reset_date': config.reset_date
                    }
                    for provider, config in ch.api_configurations.items()
                },
                'created_at': ch.created_at,
                'updated_at': ch.updated_at
            }
            for ch in channels
        ]
        
        return jsonify({
            'success': True,
            'data': channels_data,
            'total': len(channels_data)
        })
    except Exception as e:
        logger.error(f"Failed to get channels: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/', methods=['POST'])
@cross_origin()
def add_channel():
    """Add a new channel"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['channel_name', 'gmail_account', 'gmail_app_password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        channel_id = run_async(channel_manager.add_channel(
            channel_name=data['channel_name'],
            gmail_account=data['gmail_account'],
            gmail_app_password=data['gmail_app_password']
        ))
        
        return jsonify({
            'success': True,
            'data': {
                'channel_id': channel_id,
                'message': 'Channel added successfully'
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Failed to add channel: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>', methods=['GET'])
@cross_origin()
def get_channel(channel_id):
    """Get specific channel"""
    try:
        channel = run_async(channel_manager.get_channel(channel_id))
        
        if not channel:
            return jsonify({
                'success': False,
                'error': 'Channel not found'
            }), 404
        
        channel_data = {
            'channel_id': channel.channel_id,
            'channel_name': channel.channel_name,
            'gmail_account': channel.gmail_account,
            'status': channel.status.value,
            'api_configurations': {
                provider: {
                    'provider': config.provider.value,
                    'monthly_limit': config.monthly_limit,
                    'current_usage': config.current_usage,
                    'is_active': config.is_active,
                    'reset_date': config.reset_date
                }
                for provider, config in channel.api_configurations.items()
            },
            'settings': channel.settings,
            'created_at': channel.created_at,
            'updated_at': channel.updated_at
        }
        
        return jsonify({
            'success': True,
            'data': channel_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get channel {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>', methods=['DELETE'])
@cross_origin()
def remove_channel(channel_id):
    """Remove a channel"""
    try:
        success = run_async(channel_manager.remove_channel(channel_id))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Channel not found or could not be removed'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Channel removed successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to remove channel {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>/status', methods=['PUT'])
@cross_origin()
def update_channel_status(channel_id):
    """Update channel status"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Status not provided'
            }), 400
        
        try:
            status = ChannelStatus(data['status'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid status value'
            }), 400
        
        success = run_async(channel_manager.update_channel_status(channel_id, status))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Channel not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Channel status updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to update channel status {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>/api-config', methods=['POST'])
@cross_origin()
def update_api_config(channel_id):
    """Update API configuration for a channel"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['provider', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        try:
            provider = APIProviderType(data['provider'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid API provider'
            }), 400
        
        success = run_async(channel_manager.update_channel_api_config(
            channel_id=channel_id,
            provider=provider,
            api_key=data['api_key'],
            secret_key=data.get('secret_key'),
            oauth_credentials=data.get('oauth_credentials'),
            monthly_limit=data.get('monthly_limit', 1000)
        ))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update API configuration'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'API configuration updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to update API config for {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>/api-limits', methods=['GET'])
@cross_origin()
def get_api_limits(channel_id):
    """Get API limits for a channel"""
    try:
        provider_param = request.args.get('provider')
        
        if not provider_param:
            # Get all API limits
            channel = run_async(channel_manager.get_channel(channel_id))
            if not channel:
                return jsonify({
                    'success': False,
                    'error': 'Channel not found'
                }), 404
            
            limits = {}
            for provider_str in channel.api_configurations.keys():
                try:
                    provider = APIProviderType(provider_str)
                    limits[provider_str] = run_async(
                        channel_manager.check_api_limit(channel_id, provider)
                    )
                except ValueError:
                    continue
            
            return jsonify({
                'success': True,
                'data': limits
            })
        else:
            # Get specific provider limit
            try:
                provider = APIProviderType(provider_param)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid API provider'
                }), 400
            
            limit_info = run_async(channel_manager.check_api_limit(channel_id, provider))
            
            return jsonify({
                'success': True,
                'data': limit_info
            })
        
    except Exception as e:
        logger.error(f"Failed to get API limits for {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>/analytics', methods=['GET'])
@cross_origin()
def get_channel_analytics(channel_id):
    """Get analytics for a channel"""
    try:
        metric_name = request.args.get('metric')
        days = int(request.args.get('days', 30))
        
        analytics = run_async(channel_manager.get_channel_analytics(
            channel_id=channel_id,
            metric_name=metric_name,
            days=days
        ))
        
        return jsonify({
            'success': True,
            'data': analytics
        })
        
    except Exception as e:
        logger.error(f"Failed to get analytics for {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>/video-queue', methods=['POST'])
@cross_origin()
def add_video_to_queue(channel_id):
    """Add video to channel's content queue"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        required_fields = ['video_title', 'video_description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        success = run_async(channel_manager.add_video_to_queue(
            channel_id=channel_id,
            video_title=data['video_title'],
            video_description=data['video_description'],
            video_tags=data.get('video_tags', []),
            scheduled_time=data.get('scheduled_time')
        ))
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to add video to queue'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Video added to queue successfully'
        })
        
    except Exception as e:
        logger.error(f"Failed to add video to queue for {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Third-party Integration Routes
@channel_bp.route('/<channel_id>/integrations/vidiq/keywords', methods=['POST'])
@cross_origin()
def get_vidiq_keywords(channel_id):
    """Get keyword suggestions from VidIQ"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                'success': False,
                'error': 'Topic not provided'
            }), 400
        
        # Get channel API config for VidIQ
        channel = run_async(channel_manager.get_channel(channel_id))
        if not channel:
            return jsonify({
                'success': False,
                'error': 'Channel not found'
            }), 404
        
        if APIProviderType.VIDIQ.value not in channel.api_configurations:
            return jsonify({
                'success': False,
                'error': 'VidIQ API not configured for this channel'
            }), 400
        
        api_config = channel.api_configurations[APIProviderType.VIDIQ.value]
        vidiq = VidIQIntegration(api_config.api_key)
        
        keywords = run_async(vidiq.get_keyword_suggestions(channel_id, data['topic']))
        
        return jsonify({
            'success': True,
            'data': keywords
        })
        
    except Exception as e:
        logger.error(f"Failed to get VidIQ keywords for {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>/integrations/socialblade/stats', methods=['GET'])
@cross_origin()
def get_socialblade_stats(channel_id):
    """Get Social Blade statistics"""
    try:
        # Get channel API config for Social Blade
        channel = run_async(channel_manager.get_channel(channel_id))
        if not channel:
            return jsonify({
                'success': False,
                'error': 'Channel not found'
            }), 404
        
        if APIProviderType.SOCIAL_BLADE.value not in channel.api_configurations:
            return jsonify({
                'success': False,
                'error': 'Social Blade API not configured for this channel'
            }), 400
        
        api_config = channel.api_configurations[APIProviderType.SOCIAL_BLADE.value]
        socialblade = SocialBladeIntegration(api_config.api_key)
        
        stats = run_async(socialblade.get_channel_stats(channel_id))
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Failed to get Social Blade stats for {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@channel_bp.route('/<channel_id>/integrations/tubebuddy/upload-time', methods=['GET'])
@cross_origin()
def get_best_upload_time(channel_id):
    """Get optimal upload time from TubeBuddy-like analysis"""
    try:
        # Get channel API config for TubeBuddy
        channel = run_async(channel_manager.get_channel(channel_id))
        if not channel:
            return jsonify({
                'success': False,
                'error': 'Channel not found'
            }), 404
        
        if APIProviderType.TUBEBUDDY.value not in channel.api_configurations:
            return jsonify({
                'success': False,
                'error': 'TubeBuddy API not configured for this channel'
            }), 400
        
        api_config = channel.api_configurations[APIProviderType.TUBEBUDDY.value]
        tubebuddy = TubeBuddyIntegration(api_config.api_key)
        
        upload_time = run_async(tubebuddy.get_best_upload_time(channel_id))
        
        return jsonify({
            'success': True,
            'data': upload_time
        })
        
    except Exception as e:
        logger.error(f"Failed to get upload time for {channel_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Bulk Operations
@channel_bp.route('/bulk/status', methods=['PUT'])
@cross_origin()
def bulk_update_status():
    """Update status for multiple channels"""
    try:
        data = request.get_json()
        
        if not data or 'channel_ids' not in data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Channel IDs and status are required'
            }), 400
        
        try:
            status = ChannelStatus(data['status'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid status value'
            }), 400
        
        results = []
        for channel_id in data['channel_ids']:
            success = run_async(channel_manager.update_channel_status(channel_id, status))
            results.append({
                'channel_id': channel_id,
                'success': success
            })
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Failed to bulk update status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Initialize the channel manager
def init_channel_manager():
    """Initialize the channel manager"""
    try:
        run_async(channel_manager.initialize())
        logger.info("Channel manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize channel manager: {str(e)}")
        raise