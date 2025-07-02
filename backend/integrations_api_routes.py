"""
API Routes for Third-Party Integrations
VidIQ, Social Blade, and TubeBuddy functionality
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import asyncio
import logging
from typing import Dict, Any

from third_party_integrations import integrations_manager

logger = logging.getLogger(__name__)

# Create Blueprint
integrations_bp = Blueprint('integrations', __name__, url_prefix='/api/v2/integrations')

# Utility function to run async functions in sync context
def run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@integrations_bp.route('/status', methods=['GET'])
@cross_origin()
def get_integration_status():
    """Get status of all third-party integrations"""
    try:
        status = run_async(integrations_manager.get_integration_status())
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Failed to get integration status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/comprehensive-analysis/<channel_id>', methods=['GET'])
@cross_origin()
def get_comprehensive_analysis(channel_id):
    """Get comprehensive channel analysis from all integrations"""
    try:
        analysis = run_async(integrations_manager.comprehensive_channel_analysis(channel_id))
        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        logger.error(f"Failed to get comprehensive analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/keyword-research', methods=['POST'])
@cross_origin()
def get_keyword_research():
    """Get comprehensive keyword research"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        topic = data['topic']
        channel_id = data.get('channel_id', '')
        
        research = run_async(integrations_manager.keyword_research_suite(topic, channel_id))
        
        return jsonify({
            'success': True,
            'data': research
        })
        
    except Exception as e:
        logger.error(f"Failed to get keyword research: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/competitor-intelligence/<channel_id>', methods=['POST'])
@cross_origin()
def get_competitor_intelligence(channel_id):
    """Get competitor intelligence analysis"""
    try:
        data = request.get_json()
        
        competitors = data.get('competitors', []) if data else []
        
        intelligence = run_async(integrations_manager.competitor_intelligence(channel_id, competitors))
        
        return jsonify({
            'success': True,
            'data': intelligence
        })
        
    except Exception as e:
        logger.error(f"Failed to get competitor intelligence: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/video-optimization', methods=['POST'])
@cross_origin()
def get_video_optimization():
    """Get comprehensive video optimization recommendations"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Video data is required'
            }), 400
        
        optimization = run_async(integrations_manager.video_optimization_suite(data))
        
        return jsonify({
            'success': True,
            'data': optimization
        })
        
    except Exception as e:
        logger.error(f"Failed to get video optimization: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# VidIQ Specific Routes
@integrations_bp.route('/vidiq/keywords/<channel_id>', methods=['POST'])
@cross_origin()
def get_vidiq_keywords(channel_id):
    """Get VidIQ keyword suggestions"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        if not integrations_manager.vidiq:
            return jsonify({
                'success': False,
                'error': 'VidIQ integration not available'
            }), 503
        
        keywords = run_async(integrations_manager.vidiq.get_keyword_suggestions(channel_id, data['topic']))
        
        return jsonify({
            'success': True,
            'data': [k.to_dict() for k in keywords]
        })
        
    except Exception as e:
        logger.error(f"Failed to get VidIQ keywords: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/vidiq/seo-analysis/<video_id>', methods=['GET'])
@cross_origin()
def get_vidiq_seo_analysis(video_id):
    """Get VidIQ SEO analysis for video"""
    try:
        if not integrations_manager.vidiq:
            return jsonify({
                'success': False,
                'error': 'VidIQ integration not available'
            }), 503
        
        analysis = run_async(integrations_manager.vidiq.analyze_video_seo(video_id))
        
        return jsonify({
            'success': True,
            'data': analysis.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get VidIQ SEO analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/vidiq/trending-topics', methods=['GET'])
@cross_origin()
def get_vidiq_trending():
    """Get VidIQ trending topics"""
    try:
        if not integrations_manager.vidiq:
            return jsonify({
                'success': False,
                'error': 'VidIQ integration not available'
            }), 503
        
        category = request.args.get('category', 'general')
        
        trending = run_async(integrations_manager.vidiq.get_trending_topics(category))
        
        return jsonify({
            'success': True,
            'data': trending
        })
        
    except Exception as e:
        logger.error(f"Failed to get VidIQ trending topics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/vidiq/growth-insights/<channel_id>', methods=['GET'])
@cross_origin()
def get_vidiq_growth_insights(channel_id):
    """Get VidIQ growth insights"""
    try:
        if not integrations_manager.vidiq:
            return jsonify({
                'success': False,
                'error': 'VidIQ integration not available'
            }), 503
        
        insights = run_async(integrations_manager.vidiq.get_channel_growth_insights(channel_id))
        
        return jsonify({
            'success': True,
            'data': insights
        })
        
    except Exception as e:
        logger.error(f"Failed to get VidIQ growth insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Social Blade Specific Routes
@integrations_bp.route('/socialblade/channel-stats/<channel_id>', methods=['GET'])
@cross_origin()
def get_socialblade_stats(channel_id):
    """Get Social Blade channel statistics"""
    try:
        if not integrations_manager.socialblade:
            return jsonify({
                'success': False,
                'error': 'Social Blade integration not available'
            }), 503
        
        stats = run_async(integrations_manager.socialblade.get_channel_stats(channel_id))
        
        return jsonify({
            'success': True,
            'data': stats.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get Social Blade stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/socialblade/growth-metrics/<channel_id>', methods=['GET'])
@cross_origin()
def get_socialblade_growth(channel_id):
    """Get Social Blade growth metrics"""
    try:
        if not integrations_manager.socialblade:
            return jsonify({
                'success': False,
                'error': 'Social Blade integration not available'
            }), 503
        
        metrics = run_async(integrations_manager.socialblade.get_growth_metrics(channel_id))
        
        return jsonify({
            'success': True,
            'data': metrics.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get Social Blade growth metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/socialblade/trending-content', methods=['GET'])
@cross_origin()
def get_socialblade_trending():
    """Get Social Blade trending content"""
    try:
        if not integrations_manager.socialblade:
            return jsonify({
                'success': False,
                'error': 'Social Blade integration not available'
            }), 503
        
        niche = request.args.get('niche', 'general')
        region = request.args.get('region', 'US')
        
        trending = run_async(integrations_manager.socialblade.get_trending_content(niche, region))
        
        return jsonify({
            'success': True,
            'data': trending
        })
        
    except Exception as e:
        logger.error(f"Failed to get Social Blade trending content: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/socialblade/full-report/<channel_id>', methods=['GET'])
@cross_origin()
def get_socialblade_report(channel_id):
    """Get comprehensive Social Blade report"""
    try:
        if not integrations_manager.socialblade:
            return jsonify({
                'success': False,
                'error': 'Social Blade integration not available'
            }), 503
        
        report = run_async(integrations_manager.socialblade.generate_full_report(channel_id))
        
        return jsonify({
            'success': True,
            'data': report.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get Social Blade report: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# TubeBuddy Specific Routes
@integrations_bp.route('/tubebuddy/upload-time/<channel_id>', methods=['GET'])
@cross_origin()
def get_tubebuddy_upload_time(channel_id):
    """Get TubeBuddy optimal upload time analysis"""
    try:
        if not integrations_manager.tubebuddy:
            return jsonify({
                'success': False,
                'error': 'TubeBuddy integration not available'
            }), 503
        
        analysis = run_async(integrations_manager.tubebuddy.get_best_upload_time(channel_id))
        
        return jsonify({
            'success': True,
            'data': analysis.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get TubeBuddy upload time: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/tubebuddy/tag-suggestions', methods=['POST'])
@cross_origin()
def get_tubebuddy_tags():
    """Get TubeBuddy tag suggestions"""
    try:
        if not integrations_manager.tubebuddy:
            return jsonify({
                'success': False,
                'error': 'TubeBuddy integration not available'
            }), 503
        
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({
                'success': False,
                'error': 'Video title is required'
            }), 400
        
        title = data['title']
        description = data.get('description', '')
        
        suggestions = run_async(integrations_manager.tubebuddy.get_tag_suggestions(title, description))
        
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in suggestions]
        })
        
    except Exception as e:
        logger.error(f"Failed to get TubeBuddy tag suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/tubebuddy/thumbnail-analysis', methods=['POST'])
@cross_origin()
def get_tubebuddy_thumbnail_analysis():
    """Get TubeBuddy thumbnail analysis"""
    try:
        if not integrations_manager.tubebuddy:
            return jsonify({
                'success': False,
                'error': 'TubeBuddy integration not available'
            }), 503
        
        data = request.get_json()
        
        thumbnail_url = data.get('thumbnail_url') if data else None
        video_title = data.get('title', '') if data else ''
        
        analysis = run_async(integrations_manager.tubebuddy.analyze_thumbnail(thumbnail_url, video_title))
        
        return jsonify({
            'success': True,
            'data': analysis.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get TubeBuddy thumbnail analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/tubebuddy/channel-health/<channel_id>', methods=['GET'])
@cross_origin()
def get_tubebuddy_channel_health(channel_id):
    """Get TubeBuddy channel health score"""
    try:
        if not integrations_manager.tubebuddy:
            return jsonify({
                'success': False,
                'error': 'TubeBuddy integration not available'
            }), 503
        
        health = run_async(integrations_manager.tubebuddy.get_channel_health_score(channel_id))
        
        return jsonify({
            'success': True,
            'data': health
        })
        
    except Exception as e:
        logger.error(f"Failed to get TubeBuddy channel health: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@integrations_bp.route('/tubebuddy/content-optimization', methods=['POST'])
@cross_origin()
def get_tubebuddy_optimization():
    """Get TubeBuddy content optimization"""
    try:
        if not integrations_manager.tubebuddy:
            return jsonify({
                'success': False,
                'error': 'TubeBuddy integration not available'
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Video data is required'
            }), 400
        
        optimization = run_async(integrations_manager.tubebuddy.optimize_content(data))
        
        return jsonify({
            'success': True,
            'data': optimization.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Failed to get TubeBuddy optimization: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Bulk Operations
@integrations_bp.route('/bulk/video-optimization', methods=['POST'])
@cross_origin()
def bulk_video_optimization():
    """Bulk video optimization"""
    try:
        if not integrations_manager.tubebuddy:
            return jsonify({
                'success': False,
                'error': 'TubeBuddy integration not available'
            }), 503
        
        data = request.get_json()
        
        if not data or 'videos' not in data:
            return jsonify({
                'success': False,
                'error': 'Video list is required'
            }), 400
        
        videos = data['videos']
        
        optimizations = run_async(integrations_manager.tubebuddy.bulk_optimize_videos(videos))
        
        return jsonify({
            'success': True,
            'data': optimizations
        })
        
    except Exception as e:
        logger.error(f"Failed to perform bulk optimization: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Analytics Dashboard
@integrations_bp.route('/dashboard/<channel_id>', methods=['GET'])
@cross_origin()
def get_analytics_dashboard(channel_id):
    """Get comprehensive analytics dashboard data"""
    try:
        # Get data from all sources
        dashboard_data = run_async(integrations_manager.comprehensive_channel_analysis(channel_id))
        
        # Add additional dashboard-specific data
        dashboard_data['dashboard_widgets'] = {
            'growth_summary': {
                'enabled': True,
                'data_source': 'socialblade'
            },
            'keyword_performance': {
                'enabled': True,
                'data_source': 'vidiq'
            },
            'optimization_score': {
                'enabled': True,
                'data_source': 'tubebuddy'
            },
            'competitor_tracking': {
                'enabled': True,
                'data_source': 'multiple'
            }
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get analytics dashboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Initialize integrations
def init_integrations(api_keys: Dict[str, str] = None):
    """Initialize integrations with API keys"""
    try:
        run_async(integrations_manager.initialize(api_keys))
        logger.info("Third-party integrations initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize integrations: {str(e)}")
        raise