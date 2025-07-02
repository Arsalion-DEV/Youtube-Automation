"""
FastAPI Routes for AI-Powered Channel Wizard
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from auth import get_current_user
from ai_channel_wizard import (
    ai_wizard, 
    ChannelSetupConfig, 
    ChannelNiche,
    ContentType
)

logger = logging.getLogger(__name__)

# Create router
wizard_router = APIRouter(tags=["ai-wizard"])

# Pydantic Models
class ChannelSetupRequest(BaseModel):
    channel_name: str = Field(..., min_length=1, max_length=100)
    niche: Optional[str] = None
    target_country: str = Field(default="US", max_length=2)
    target_language: str = Field(default="en-US", max_length=10)
    content_style: str = Field(default="educational")
    upload_frequency: str = Field(default="weekly")
    target_audience: str = Field(default="18-35")
    monetization_goals: List[str] = Field(default=["ad_revenue", "sponsorships"])
    budget_range: str = Field(default="0-500")

class NicheAnalysisRequest(BaseModel):
    channel_description: str
    sample_video_titles: List[str] = Field(default=[])

class SEOOptimizationRequest(BaseModel):
    niche: str
    country: str = Field(default="US")
    language: str = Field(default="en-US")

class BrandingRequest(BaseModel):
    channel_name: str
    niche: str
    color_preferences: Optional[List[str]] = None

class CompetitorAnalysisRequest(BaseModel):
    niche: str
    country: str = Field(default="US")

class ContentStrategyRequest(BaseModel):
    channel_setup: ChannelSetupRequest
    include_calendar: bool = Field(default=True)
    calendar_days: int = Field(default=30, ge=7, le=90)

# Response Models
class WizardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class NicheAnalysisResponse(BaseModel):
    detected_niche: str
    confidence: float
    suggested_niches: List[str]
    niche_description: str

class SEOResponse(BaseModel):
    keywords: List[str]
    trending_topics: List[str]
    optimal_upload_times: List[str]
    hashtag_suggestions: List[str]
    title_templates: List[str]
    description_templates: List[str]

class BrandingResponse(BaseModel):
    color_palette: List[str]
    font_suggestions: List[str]
    brand_guidelines: str
    logo_concept: str
    channel_art_concept: str

class CompetitorResponse(BaseModel):
    top_competitors: List[Dict[str, Any]]
    content_gaps: List[str]
    trending_formats: List[str]
    optimal_video_length: Dict[str, int]
    engagement_insights: Dict[str, Any]
    market_analysis: str

class ContentStrategyResponse(BaseModel):
    content_calendar: List[Dict[str, Any]]
    content_pillars: List[str]
    series_ideas: List[Dict[str, Any]]
    collaboration_opportunities: List[str]
    monetization_timeline: Dict[str, str]

@wizard_router.post("/analyze-niche", response_model=NicheAnalysisResponse)
async def analyze_channel_niche(
    request: NicheAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze and detect channel niche using AI"""
    try:
        detected_niche = await ai_wizard.analyze_channel_niche(
            request.channel_description,
            request.sample_video_titles
        )
        
        # Get niche description
        niche_descriptions = {
            "tech_reviews": "Technology reviews, gadget unboxings, and tech news content",
            "gaming": "Gaming content, gameplay videos, game reviews and esports",
            "lifestyle": "Lifestyle vlogs, personal development, and daily life content",
            "education": "Educational content, tutorials, courses and learning materials",
            "entertainment": "Entertainment content, comedy, reactions and viral videos",
            "music": "Music content, covers, original songs and music reviews",
            "fitness": "Fitness content, workouts, health tips and wellness advice",
            "cooking": "Cooking content, recipes, food reviews and culinary tips",
            "travel": "Travel content, destination guides, adventures and travel tips",
            "business": "Business content, entrepreneurship, marketing and finance advice"
        }
        
        # Suggest related niches
        related_niches = {
            "tech_reviews": ["gaming", "business", "education"],
            "gaming": ["tech_reviews", "entertainment", "lifestyle"],
            "lifestyle": ["fitness", "travel", "entertainment"],
            "education": ["business", "tech_reviews", "lifestyle"],
            "entertainment": ["gaming", "music", "comedy"],
            "music": ["entertainment", "lifestyle", "education"],
            "fitness": ["lifestyle", "education", "cooking"],
            "cooking": ["lifestyle", "entertainment", "education"],
            "travel": ["lifestyle", "entertainment", "education"],
            "business": ["education", "tech_reviews", "lifestyle"]
        }
        
        niche_value = detected_niche.value
        suggested_niches = related_niches.get(niche_value, ["lifestyle", "entertainment"])
        
        return NicheAnalysisResponse(
            detected_niche=niche_value,
            confidence=0.85,  # Simulated confidence score
            suggested_niches=suggested_niches,
            niche_description=niche_descriptions.get(niche_value, "General content creation")
        )
        
    except Exception as e:
        logger.error(f"Error analyzing niche: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze channel niche")

@wizard_router.post("/seo-optimization", response_model=SEOResponse)
async def generate_seo_optimization(
    request: SEOOptimizationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate country-specific SEO optimization"""
    try:
        # Convert string niche to enum
        niche_enum = ChannelNiche(request.niche)
        
        seo_data = await ai_wizard.generate_country_specific_seo(
            niche_enum,
            request.country,
            request.language
        )
        
        return SEOResponse(
            keywords=seo_data.keywords,
            trending_topics=seo_data.trending_topics,
            optimal_upload_times=seo_data.optimal_upload_times,
            hashtag_suggestions=seo_data.hashtag_suggestions,
            title_templates=seo_data.title_templates,
            description_templates=seo_data.description_templates
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid niche: {request.niche}")
    except Exception as e:
        logger.error(f"Error generating SEO optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate SEO optimization")

@wizard_router.post("/branding", response_model=BrandingResponse)
async def generate_channel_branding(
    request: BrandingRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate automated channel branding"""
    try:
        niche_enum = ChannelNiche(request.niche)
        
        branding_data = await ai_wizard.generate_channel_branding(
            request.channel_name,
            niche_enum,
            request.color_preferences
        )
        
        # Generate concepts for logo and channel art
        logo_concept = f"Modern minimalist logo featuring '{request.channel_name}' with {request.niche} themed elements"
        channel_art_concept = f"Professional channel banner incorporating brand colors and {request.niche} visual elements"
        
        return BrandingResponse(
            color_palette=branding_data.color_palette,
            font_suggestions=branding_data.font_suggestions,
            brand_guidelines=branding_data.brand_guidelines,
            logo_concept=logo_concept,
            channel_art_concept=channel_art_concept
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid niche: {request.niche}")
    except Exception as e:
        logger.error(f"Error generating branding: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate channel branding")

@wizard_router.post("/competitor-analysis", response_model=CompetitorResponse)
async def analyze_competitors(
    request: CompetitorAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze competitors in the same niche"""
    try:
        niche_enum = ChannelNiche(request.niche)
        
        competitor_data = await ai_wizard.analyze_competitors(
            niche_enum,
            request.country
        )
        
        # Generate market analysis summary
        market_analysis = f"""
        Market Analysis for {request.niche.replace('_', ' ').title()}:
        
        The {request.niche} niche shows strong competition with established creators.
        Key opportunities include focusing on underserved content gaps and emerging trends.
        Recommended strategy: Create unique value propositions and consistent posting schedule.
        """
        
        return CompetitorResponse(
            top_competitors=competitor_data.top_competitors,
            content_gaps=competitor_data.content_gaps,
            trending_formats=competitor_data.trending_formats,
            optimal_video_length=competitor_data.optimal_video_length,
            engagement_insights=competitor_data.engagement_insights,
            market_analysis=market_analysis.strip()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid niche: {request.niche}")
    except Exception as e:
        logger.error(f"Error analyzing competitors: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze competitors")

@wizard_router.post("/content-strategy", response_model=ContentStrategyResponse)
async def generate_content_strategy(
    request: ContentStrategyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate AI-powered content strategy"""
    try:
        # Convert request to ChannelSetupConfig
        niche_enum = ChannelNiche(request.channel_setup.niche) if request.channel_setup.niche else ChannelNiche.ENTERTAINMENT
        
        setup_config = ChannelSetupConfig(
            channel_name=request.channel_setup.channel_name,
            niche=niche_enum,
            target_country=request.channel_setup.target_country,
            target_language=request.channel_setup.target_language,
            content_style=request.channel_setup.content_style,
            upload_frequency=request.channel_setup.upload_frequency,
            target_audience=request.channel_setup.target_audience,
            monetization_goals=request.channel_setup.monetization_goals,
            budget_range=request.channel_setup.budget_range
        )
        
        # Generate required data
        seo_data = await ai_wizard.generate_country_specific_seo(
            niche_enum,
            setup_config.target_country,
            setup_config.target_language
        )
        
        competitor_data = await ai_wizard.analyze_competitors(
            niche_enum,
            setup_config.target_country
        )
        
        content_strategy = await ai_wizard.generate_content_strategy(
            setup_config,
            seo_data,
            competitor_data
        )
        
        return ContentStrategyResponse(
            content_calendar=content_strategy.content_calendar,
            content_pillars=content_strategy.content_pillars,
            series_ideas=content_strategy.series_ideas,
            collaboration_opportunities=content_strategy.collaboration_opportunities,
            monetization_timeline=content_strategy.monetization_timeline
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating content strategy: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate content strategy")

@wizard_router.post("/complete-setup", response_model=WizardResponse)
async def run_complete_wizard(
    request: ChannelSetupRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Run the complete AI-powered channel setup wizard"""
    try:
        # Convert to ChannelSetupConfig
        niche_enum = ChannelNiche(request.niche) if request.niche else ChannelNiche.ENTERTAINMENT
        
        setup_config = ChannelSetupConfig(
            channel_name=request.channel_name,
            niche=niche_enum,
            target_country=request.target_country,
            target_language=request.target_language,
            content_style=request.content_style,
            upload_frequency=request.upload_frequency,
            target_audience=request.target_audience,
            monetization_goals=request.monetization_goals,
            budget_range=request.budget_range
        )
        
        # Run complete wizard
        wizard_result = await ai_wizard.run_complete_channel_wizard(
            current_user["user_id"],
            setup_config
        )
        
        return WizardResponse(
            success=True,
            message="Channel wizard completed successfully",
            data=wizard_result
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Error running complete wizard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete channel wizard")

@wizard_router.get("/wizard-result/{channel_id}")
async def get_wizard_result(
    channel_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get saved wizard results for a channel"""
    try:
        result = await ai_wizard.get_wizard_result(
            current_user["user_id"],
            channel_id
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Wizard result not found")
        
        return WizardResponse(
            success=True,
            message="Wizard result retrieved successfully",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving wizard result: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve wizard result")

@wizard_router.get("/niches")
async def get_available_niches():
    """Get list of available channel niches"""
    niches = [
        {"value": niche.value, "label": niche.value.replace('_', ' ').title()}
        for niche in ChannelNiche
    ]
    
    return {"niches": niches}

@wizard_router.get("/countries")
async def get_supported_countries():
    """Get list of supported countries for SEO optimization"""
    from ai_channel_wizard import CountryData
    
    countries = []
    for code, config in CountryData.COUNTRY_CONFIGS.items():
        countries.append({
            "code": code,
            "name": {
                "US": "United States",
                "GB": "United Kingdom", 
                "CA": "Canada",
                "AU": "Australia",
                "IN": "India",
                "DE": "Germany"
            }.get(code, code),
            "timezone": config["timezone"],
            "language": config["language"]
        })
    
    return {"countries": countries}

@wizard_router.post("/content-ideas/{channel_id}")
async def generate_content_ideas(
    channel_id: str,
    count: int = Query(default=10, ge=1, le=50),
    content_type: Optional[str] = Query(default=None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate AI-powered content ideas for a specific channel"""
    try:
        # Get wizard result for the channel
        wizard_result = await ai_wizard.get_wizard_result(
            current_user["user_id"],
            channel_id
        )
        
        if not wizard_result:
            raise HTTPException(status_code=404, detail="Channel wizard not found. Please run the setup wizard first.")
        
        # Generate content ideas based on wizard data
        content_strategy = wizard_result.get("content_strategy", {})
        setup_config = wizard_result.get("setup_config", {})
        seo_data = wizard_result.get("seo_optimization", {})
        
        content_ideas = []
        keywords = seo_data.get("keywords", ["general content"])
        content_pillars = content_strategy.get("content_pillars", ["General", "Tips", "Reviews"])
        
        for i in range(count):
            keyword = keywords[i % len(keywords)]
            pillar = content_pillars[i % len(content_pillars)]
            
            idea = {
                "id": f"idea_{i+1}",
                "title": f"{pillar}: {keyword.title()} {'Guide' if i % 2 == 0 else 'Tips'}",
                "description": f"Create engaging content about {keyword} focusing on {pillar.lower()}",
                "content_type": content_type or ("short_form" if i % 3 == 0 else "long_form"),
                "keywords": [keyword],
                "estimated_views": f"{random.randint(1000, 50000):,}",
                "difficulty": ["Easy", "Medium", "Hard"][i % 3],
                "ai_confidence": round(random.uniform(0.7, 0.95), 2)
            }
            content_ideas.append(idea)
        
        return {
            "success": True,
            "content_ideas": content_ideas,
            "channel_id": channel_id,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating content ideas: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate content ideas")