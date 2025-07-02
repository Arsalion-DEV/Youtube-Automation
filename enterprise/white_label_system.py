"""
White Label Solutions System
Enables customers to rebrand and customize the platform as their own
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid
import hashlib
from pathlib import Path

import aiofiles
from PIL import Image, ImageDraw, ImageFont
import qrcode
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class WhiteLabelManager:
    """Manages white-label customizations and branding"""
    
    def __init__(self):
        self.base_path = "/app/white_label"
        self.template_path = f"{self.base_path}/templates"
        self.assets_path = f"{self.base_path}/assets"
        self.custom_path = f"{self.base_path}/custom"
        
        # Ensure directories exist
        Path(self.template_path).mkdir(parents=True, exist_ok=True)
        Path(self.assets_path).mkdir(parents=True, exist_ok=True)
        Path(self.custom_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 for template rendering
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.template_path),
            autoescape=True
        )
    
    async def create_white_label_instance(
        self,
        organization_id: str,
        branding_config: Dict[str, Any],
        domain_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new white-label instance"""
        try:
            instance_id = str(uuid.uuid4())
            
            # Validate branding configuration
            required_fields = ["company_name", "logo_url", "primary_color", "secondary_color"]
            for field in required_fields:
                if field not in branding_config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create instance directory
            instance_path = f"{self.custom_path}/{instance_id}"
            Path(instance_path).mkdir(parents=True, exist_ok=True)
            
            # Generate configuration
            config = {
                "instance_id": instance_id,
                "organization_id": organization_id,
                "created_at": datetime.utcnow().isoformat(),
                "branding": branding_config,
                "domain": domain_config or {},
                "features": {
                    "custom_domain": domain_config is not None,
                    "custom_email": branding_config.get("email_domain") is not None,
                    "custom_support": branding_config.get("support_config") is not None,
                    "custom_onboarding": True,
                    "white_label_mobile_app": False  # Premium feature
                },
                "status": "active"
            }
            
            # Save configuration
            config_path = f"{instance_path}/config.json"
            async with aiofiles.open(config_path, 'w') as f:
                await f.write(json.dumps(config, indent=2))
            
            # Generate custom assets
            await self._generate_custom_assets(instance_id, branding_config)
            
            # Generate custom templates
            await self._generate_custom_templates(instance_id, branding_config)
            
            # Generate API configuration
            await self._generate_api_config(instance_id, branding_config)
            
            logger.info(f"White-label instance created: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"Error creating white-label instance: {e}")
            raise e
    
    async def _generate_custom_assets(
        self,
        instance_id: str,
        branding_config: Dict[str, Any]
    ):
        """Generate custom branded assets"""
        try:
            instance_path = f"{self.custom_path}/{instance_id}"
            assets_path = f"{instance_path}/assets"
            Path(assets_path).mkdir(exist_ok=True)
            
            # Generate favicon
            await self._generate_favicon(
                assets_path,
                branding_config.get("logo_url"),
                branding_config.get("primary_color", "#1f2937")
            )
            
            # Generate email templates
            await self._generate_email_assets(assets_path, branding_config)
            
            # Generate social media assets
            await self._generate_social_assets(assets_path, branding_config)
            
            # Generate QR codes for mobile app downloads
            await self._generate_qr_codes(assets_path, branding_config)
            
            logger.info(f"Custom assets generated for instance: {instance_id}")
            
        except Exception as e:
            logger.error(f"Error generating custom assets: {e}")
            raise e
    
    async def _generate_favicon(
        self,
        assets_path: str,
        logo_url: Optional[str],
        primary_color: str
    ):
        """Generate custom favicon"""
        try:
            # Create a simple favicon with brand colors
            favicon = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(favicon)
            
            # Convert hex color to RGB
            color = tuple(int(primary_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            # Draw a simple branded shape
            draw.ellipse([8, 8, 56, 56], fill=color)
            draw.text((32, 32), "Y", fill="white", anchor="mm")
            
            # Save favicon
            favicon_path = f"{assets_path}/favicon.ico"
            favicon.save(favicon_path, format='ICO')
            
        except Exception as e:
            logger.error(f"Error generating favicon: {e}")
    
    async def _generate_email_assets(
        self,
        assets_path: str,
        branding_config: Dict[str, Any]
    ):
        """Generate branded email templates"""
        try:
            email_path = f"{assets_path}/email"
            Path(email_path).mkdir(exist_ok=True)
            
            # Email header with branding
            email_header = f\"\"\"
            <div style="background: {branding_config.get('primary_color', '#1f2937')}; padding: 20px; text-align: center;">
                <img src="{branding_config.get('logo_url', '')}" alt="{branding_config.get('company_name', 'Company')}" style="height: 40px;">
                <h1 style="color: white; margin: 10px 0;">{branding_config.get('company_name', 'Your Platform')}</h1>
            </div>
            \"\"\"
            
            # Save email templates
            templates = {
                "welcome.html": self._get_welcome_email_template(branding_config),
                "password_reset.html": self._get_password_reset_template(branding_config),
                "video_ready.html": self._get_video_ready_template(branding_config),
                "analytics_report.html": self._get_analytics_report_template(branding_config)
            }
            
            for template_name, content in templates.items():
                template_path = f"{email_path}/{template_name}"
                async with aiofiles.open(template_path, 'w') as f:
                    await f.write(content)
            
        except Exception as e:
            logger.error(f"Error generating email assets: {e}")
    
    async def _generate_social_assets(
        self,
        assets_path: str,
        branding_config: Dict[str, Any]
    ):
        """Generate social media branded assets"""
        try:
            social_path = f"{assets_path}/social"
            Path(social_path).mkdir(exist_ok=True)
            
            company_name = branding_config.get('company_name', 'Your Platform')
            primary_color = branding_config.get('primary_color', '#1f2937')
            
            # Convert hex to RGB
            color_rgb = tuple(int(primary_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            # Generate social media cover images
            cover_sizes = {
                "facebook_cover.png": (820, 312),
                "twitter_header.png": (1500, 500),
                "linkedin_banner.png": (1584, 396),
                "youtube_banner.png": (2560, 1440)
            }
            
            for filename, size in cover_sizes.items():
                # Create branded cover image
                cover = Image.new('RGB', size, color_rgb)
                draw = ImageDraw.Draw(cover)
                
                # Add company name
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                except:
                    font = ImageFont.load_default()
                
                # Calculate text position
                bbox = draw.textbbox((0, 0), company_name, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                
                draw.text((x, y), company_name, fill="white", font=font)
                
                # Save cover image
                cover_path = f"{social_path}/{filename}"
                cover.save(cover_path, format='PNG', quality=95)
            
        except Exception as e:
            logger.error(f"Error generating social assets: {e}")
    
    async def _generate_qr_codes(
        self,
        assets_path: str,
        branding_config: Dict[str, Any]
    ):
        """Generate QR codes for mobile app downloads"""
        try:
            qr_path = f"{assets_path}/qr"
            Path(qr_path).mkdir(exist_ok=True)
            
            # App store URLs (would be customized for white-label apps)
            app_urls = {
                "ios": f"https://apps.apple.com/app/{branding_config.get('app_id', 'youtube-automation')}",
                "android": f"https://play.google.com/store/apps/details?id={branding_config.get('package_name', 'com.youtubeautomation.app')}"
            }
            
            for platform, url in app_urls.items():
                # Create QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)
                
                # Create QR code image
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                # Save QR code
                qr_path_file = f"{qr_path}/{platform}_download.png"
                qr_img.save(qr_path_file)
            
        except Exception as e:
            logger.error(f"Error generating QR codes: {e}")
    
    async def _generate_custom_templates(
        self,
        instance_id: str,
        branding_config: Dict[str, Any]
    ):
        """Generate custom frontend templates"""
        try:
            instance_path = f"{self.custom_path}/{instance_id}"
            templates_path = f"{instance_path}/templates"
            Path(templates_path).mkdir(exist_ok=True)
            
            # Generate custom CSS with brand colors
            custom_css = self._generate_custom_css(branding_config)
            css_path = f"{templates_path}/custom.css"
            async with aiofiles.open(css_path, 'w') as f:
                await f.write(custom_css)
            
            # Generate custom JavaScript configuration
            custom_js = self._generate_custom_js(branding_config)
            js_path = f"{templates_path}/custom.js"
            async with aiofiles.open(js_path, 'w') as f:
                await f.write(custom_js)
            
            # Generate custom HTML templates
            html_templates = {
                "login.html": self._get_custom_login_template(branding_config),
                "dashboard.html": self._get_custom_dashboard_template(branding_config),
                "footer.html": self._get_custom_footer_template(branding_config)
            }
            
            for template_name, content in html_templates.items():
                template_path = f"{templates_path}/{template_name}"
                async with aiofiles.open(template_path, 'w') as f:
                    await f.write(content)
            
        except Exception as e:
            logger.error(f"Error generating custom templates: {e}")
    
    async def _generate_api_config(
        self,
        instance_id: str,
        branding_config: Dict[str, Any]
    ):
        """Generate API configuration for white-label instance"""
        try:
            instance_path = f"{self.custom_path}/{instance_id}"
            
            # API configuration
            api_config = {
                "base_url": branding_config.get("api_base_url", "https://api.yourdomain.com"),
                "app_name": branding_config.get("company_name", "YouTube Automation"),
                "app_version": "3.0.0-white-label",
                "features": {
                    "analytics": True,
                    "team_management": True,
                    "ab_testing": True,
                    "white_label_branding": True,
                    "custom_domain": branding_config.get("custom_domain") is not None
                },
                "limits": {
                    "videos_per_month": branding_config.get("video_limit", 1000),
                    "team_members": branding_config.get("team_limit", 50),
                    "storage_gb": branding_config.get("storage_limit", 500)
                },
                "integrations": {
                    "youtube": True,
                    "tiktok": True,
                    "instagram": True,
                    "facebook": True,
                    "twitter": True,
                    "linkedin": True
                },
                "support": {
                    "email": branding_config.get("support_email", "support@yourdomain.com"),
                    "phone": branding_config.get("support_phone"),
                    "chat": branding_config.get("chat_enabled", True),
                    "knowledge_base": branding_config.get("knowledge_base_url")
                }
            }
            
            # Save API configuration
            config_path = f"{instance_path}/api_config.json"
            async with aiofiles.open(config_path, 'w') as f:
                await f.write(json.dumps(api_config, indent=2))
            
        except Exception as e:
            logger.error(f"Error generating API config: {e}")
    
    def _generate_custom_css(self, branding_config: Dict[str, Any]) -> str:
        """Generate custom CSS with brand colors"""
        primary = branding_config.get('primary_color', '#1f2937')
        secondary = branding_config.get('secondary_color', '#374151')
        accent = branding_config.get('accent_color', '#3b82f6')
        
        return f\"\"\"
/* Custom White-Label CSS */
:root {{
    --primary-color: {primary};
    --secondary-color: {secondary};
    --accent-color: {accent};
    --brand-font: '{branding_config.get('font_family', 'Inter')}', sans-serif;
}}

/* Override default theme colors */
.bg-primary {{ background-color: var(--primary-color) !important; }}
.text-primary {{ color: var(--primary-color) !important; }}
.border-primary {{ border-color: var(--primary-color) !important; }}

.bg-secondary {{ background-color: var(--secondary-color) !important; }}
.text-secondary {{ color: var(--secondary-color) !important; }}

.bg-accent {{ background-color: var(--accent-color) !important; }}
.text-accent {{ color: var(--accent-color) !important; }}

/* Custom buttons */
.btn-primary {{
    background-color: var(--primary-color);
    border-color: var(--primary-color);
    font-family: var(--brand-font);
}}

.btn-primary:hover {{
    background-color: var(--secondary-color);
    border-color: var(--secondary-color);
}}

/* Custom navigation */
.navbar-brand {{
    font-family: var(--brand-font);
    font-weight: 700;
}}

/* Custom forms */
.form-control:focus {{
    border-color: var(--accent-color);
    box-shadow: 0 0 0 0.2rem rgba({', '.join([str(int(accent.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4)])}, 0.25);
}}

/* Custom animations */
@keyframes brandPulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.7; }}
}}

.brand-pulse {{
    animation: brandPulse 2s ease-in-out infinite;
}}
\"\"\"
    
    def _generate_custom_js(self, branding_config: Dict[str, Any]) -> str:
        """Generate custom JavaScript configuration"""
        return f\"\"\"
// Custom White-Label Configuration
window.WhiteLabelConfig = {{
    companyName: '{branding_config.get('company_name', 'Your Platform')}',
    supportEmail: '{branding_config.get('support_email', 'support@yourdomain.com')}',
    helpUrl: '{branding_config.get('help_url', '/help')}',
    logoUrl: '{branding_config.get('logo_url', '/logo.png')}',
    theme: {{
        primaryColor: '{branding_config.get('primary_color', '#1f2937')}',
        secondaryColor: '{branding_config.get('secondary_color', '#374151')}',
        accentColor: '{branding_config.get('accent_color', '#3b82f6')}'
    }},
    features: {{
        customDomain: {str(branding_config.get('custom_domain') is not None).lower()},
        customSupport: {str(branding_config.get('support_config') is not None).lower()},
        analytics: true,
        teamManagement: true
    }}
}};

// Apply custom branding on page load
document.addEventListener('DOMContentLoaded', function() {{
    // Update page title
    document.title = window.WhiteLabelConfig.companyName + ' - YouTube Automation';
    
    // Update meta tags
    const metaTags = [
        {{ name: 'application-name', content: window.WhiteLabelConfig.companyName }},
        {{ name: 'theme-color', content: window.WhiteLabelConfig.theme.primaryColor }}
    ];
    
    metaTags.forEach(tag => {{
        let meta = document.querySelector(`meta[name="${{tag.name}}"]`);
        if (!meta) {{
            meta = document.createElement('meta');
            meta.name = tag.name;
            document.head.appendChild(meta);
        }}
        meta.content = tag.content;
    }});
}});
\"\"\"
    
    def _get_welcome_email_template(self, branding_config: Dict[str, Any]) -> str:
        """Get welcome email template"""
        company_name = branding_config.get('company_name', 'Your Platform')
        primary_color = branding_config.get('primary_color', '#1f2937')
        logo_url = branding_config.get('logo_url', '')
        
        return f\"\"\"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to {company_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: {primary_color}; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <img src="{logo_url}" alt="{company_name}" style="height: 40px; margin-bottom: 10px;">
            <h1 style="color: white; margin: 0;">Welcome to {company_name}!</h1>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
            <h2>You're all set to start creating amazing content!</h2>
            
            <p>Thanks for joining {company_name}. We're excited to help you automate your YouTube content creation and grow your channel.</p>
            
            <div style="background: white; padding: 20px; border-radius: 6px; margin: 20px 0;">
                <h3>Here's what you can do next:</h3>
                <ul>
                    <li>Connect your YouTube channel</li>
                    <li>Set up your first AI video generation</li>
                    <li>Explore our analytics dashboard</li>
                    <li>Join your team workspace</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="#" style="background: {primary_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">Get Started</a>
            </div>
            
            <p>If you have any questions, our support team is here to help at {branding_config.get('support_email', 'support@yourdomain.com')}</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #666; text-align: center;">
                {company_name} | YouTube Automation Platform<br>
                © 2024 {company_name}. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
\"\"\"
    
    def _get_password_reset_template(self, branding_config: Dict[str, Any]) -> str:
        """Get password reset email template"""
        company_name = branding_config.get('company_name', 'Your Platform')
        primary_color = branding_config.get('primary_color', '#1f2937')
        
        return f\"\"\"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reset Your Password - {company_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: {primary_color}; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0;">Password Reset Request</h1>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
            <p>We received a request to reset your password for your {company_name} account.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{{{reset_url}}}}" style="background: {primary_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
            </div>
            
            <p>This link will expire in 24 hours. If you didn't request this reset, please ignore this email.</p>
            
            <p>For security, this link can only be used once.</p>
        </div>
    </div>
</body>
</html>
\"\"\"
    
    def _get_video_ready_template(self, branding_config: Dict[str, Any]) -> str:
        """Get video ready notification template"""
        company_name = branding_config.get('company_name', 'Your Platform')
        primary_color = branding_config.get('primary_color', '#1f2937')
        
        return f\"\"\"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Your Video is Ready! - {company_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: {primary_color}; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0;">🎉 Your Video is Ready!</h1>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
            <p>Great news! Your AI-generated video "{{{{video_title}}}}" has been processed and is ready for review.</p>
            
            <div style="background: white; padding: 20px; border-radius: 6px; margin: 20px 0;">
                <h3>Video Details:</h3>
                <ul>
                    <li><strong>Title:</strong> {{{{video_title}}}}</li>
                    <li><strong>Duration:</strong> {{{{video_duration}}}}</li>
                    <li><strong>Platform:</strong> {{{{target_platform}}}}</li>
                    <li><strong>Status:</strong> Ready for Publishing</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{{{video_url}}}}" style="background: {primary_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">View & Publish</a>
            </div>
        </div>
    </div>
</body>
</html>
\"\"\"
    
    def _get_analytics_report_template(self, branding_config: Dict[str, Any]) -> str:
        """Get analytics report email template"""
        company_name = branding_config.get('company_name', 'Your Platform')
        primary_color = branding_config.get('primary_color', '#1f2937')
        
        return f\"\"\"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Weekly Analytics Report - {company_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: {primary_color}; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0;">📊 Weekly Analytics Report</h1>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px;">
            <p>Here's how your content performed this week:</p>
            
            <div style="display: flex; justify-content: space-between; margin: 20px 0;">
                <div style="background: white; padding: 15px; border-radius: 6px; text-align: center; flex: 1; margin: 0 5px;">
                    <h4 style="margin: 0; color: {primary_color};">{{{{total_views}}}}</h4>
                    <p style="margin: 5px 0; font-size: 12px;">Total Views</p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 6px; text-align: center; flex: 1; margin: 0 5px;">
                    <h4 style="margin: 0; color: {primary_color};">{{{{new_subscribers}}}}</h4>
                    <p style="margin: 5px 0; font-size: 12px;">New Subscribers</p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 6px; text-align: center; flex: 1; margin: 0 5px;">
                    <h4 style="margin: 0; color: {primary_color};">${{{{revenue}}}}</h4>
                    <p style="margin: 5px 0; font-size: 12px;">Revenue</p>
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{{{dashboard_url}}}}" style="background: {primary_color}; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">View Full Report</a>
            </div>
        </div>
    </div>
</body>
</html>
\"\"\"
    
    def _get_custom_login_template(self, branding_config: Dict[str, Any]) -> str:
        """Get custom login page template"""
        company_name = branding_config.get('company_name', 'Your Platform')
        return f\"\"\"
<!-- Custom Login Template for {company_name} -->
<div class="white-label-login">
    <div class="login-header">
        <img src="{{{{logo_url}}}}" alt="{company_name}" class="login-logo">
        <h1>{company_name}</h1>
        <p>YouTube Automation Platform</p>
    </div>
    <!-- Login form content -->
</div>
\"\"\"
    
    def _get_custom_dashboard_template(self, branding_config: Dict[str, Any]) -> str:
        """Get custom dashboard template"""
        company_name = branding_config.get('company_name', 'Your Platform')
        return f\"\"\"
<!-- Custom Dashboard Template for {company_name} -->
<div class="white-label-dashboard">
    <header class="dashboard-header">
        <h1>Welcome to {company_name}</h1>
    </header>
    <!-- Dashboard content -->
</div>
\"\"\"
    
    def _get_custom_footer_template(self, branding_config: Dict[str, Any]) -> str:
        """Get custom footer template"""
        company_name = branding_config.get('company_name', 'Your Platform')
        return f\"\"\"
<!-- Custom Footer for {company_name} -->
<footer class="white-label-footer">
    <p>&copy; 2024 {company_name}. All rights reserved.</p>
    <p>Powered by YouTube Automation Platform</p>
</footer>
\"\"\"
    
    async def get_white_label_config(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get white-label configuration"""
        try:
            config_path = f"{self.custom_path}/{instance_id}/config.json"
            async with aiofiles.open(config_path, 'r') as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error reading white-label config: {e}")
            return None
    
    async def update_white_label_config(
        self,
        instance_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update white-label configuration"""
        try:
            config = await self.get_white_label_config(instance_id)
            if not config:
                return False
            
            # Update configuration
            config.update(updates)
            config['updated_at'] = datetime.utcnow().isoformat()
            
            # Save updated configuration
            config_path = f"{self.custom_path}/{instance_id}/config.json"
            async with aiofiles.open(config_path, 'w') as f:
                await f.write(json.dumps(config, indent=2))
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating white-label config: {e}")
            return False
    
    async def delete_white_label_instance(self, instance_id: str) -> bool:
        """Delete white-label instance"""
        try:
            import shutil
            instance_path = f"{self.custom_path}/{instance_id}"
            
            if Path(instance_path).exists():
                shutil.rmtree(instance_path)
                logger.info(f"White-label instance deleted: {instance_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting white-label instance: {e}")
            return False