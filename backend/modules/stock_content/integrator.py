"""
Stock Content Integration Module
Fetches real video clips and images from Pexels and Pixabay APIs
"""

import asyncio
import logging
import os
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import hashlib
from urllib.parse import urlparse

from ..base import BaseModule

logger = logging.getLogger(__name__)

class StockContentIntegrator(BaseModule):
    """Integration with stock content providers"""
    
    def __init__(self):
        super().__init__()
        self.module_name = "stock_content"
        
        # API endpoints
        self.pexels_api_url = "https://api.pexels.com/v1"
        self.pexels_video_api_url = "https://api.pexels.com/videos"
        self.pixabay_api_url = "https://pixabay.com/api"
        self.pixabay_video_api_url = "https://pixabay.com/api/videos"
        
        # API keys
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        
        # Cache directories
        self.cache_dir = "assets/stock_cache"
        self.videos_cache_dir = "assets/stock_cache/videos"
        self.images_cache_dir = "assets/stock_cache/images"
        
        # Search categories
        self.search_categories = {
            "technology": ["technology", "computer", "digital", "coding", "software", "data", "ai"],
            "business": ["business", "office", "meeting", "corporate", "finance", "money"],
            "nature": ["nature", "forest", "ocean", "mountain", "landscape", "wildlife"],
            "people": ["people", "person", "group", "team", "working", "lifestyle"],
            "abstract": ["abstract", "background", "pattern", "texture", "geometric"],
            "science": ["science", "laboratory", "research", "experiment", "medical"],
            "education": ["education", "learning", "school", "study", "books", "classroom"],
            "travel": ["travel", "city", "architecture", "landmark", "transportation"]
        }
        
        # Content filters
        self.content_filters = {
            "safe_search": True,
            "min_width": 1280,
            "min_height": 720,
            "video_min_duration": 3,
            "video_max_duration": 30,
            "preferred_orientations": ["horizontal", "landscape"]
        }
    
    async def _setup_module(self):
        """Initialize stock content integrator"""
        await super()._setup_module()
        
        try:
            # Create cache directories
            for directory in [self.cache_dir, self.videos_cache_dir, self.images_cache_dir]:
                Path(directory).mkdir(parents=True, exist_ok=True)
            
            # Check API keys
            if not self.pexels_api_key and not self.pixabay_api_key:
                self.logger.warning("No stock content API keys found - functionality will be limited")
            
            self.logger.info("Stock Content Integrator initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize stock content integrator: {str(e)}")
            raise
    
    async def search_videos(
        self,
        query: str,
        category: Optional[str] = None,
        count: int = 5,
        duration_preference: str = "short",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for stock videos"""
        
        try:
            self.logger.info(f"Searching for videos: {query}")
            
            # Enhance query with category keywords
            enhanced_query = await self._enhance_search_query(query, category)
            
            # Search both providers
            results = []
            
            # Search Pexels videos
            if self.pexels_api_key:
                pexels_results = await self._search_pexels_videos(
                    enhanced_query, count // 2 + 1, duration_preference, **kwargs
                )
                results.extend(pexels_results)
            
            # Search Pixabay videos
            if self.pixabay_api_key:
                pixabay_results = await self._search_pixabay_videos(
                    enhanced_query, count // 2 + 1, duration_preference, **kwargs
                )
                results.extend(pixabay_results)
            
            # Filter and sort results
            filtered_results = await self._filter_video_results(results, **kwargs)
            
            # Limit to requested count
            return filtered_results[:count]
            
        except Exception as e:
            self.logger.error(f"Video search failed: {str(e)}")
            return []
    
    async def search_images(
        self,
        query: str,
        category: Optional[str] = None,
        count: int = 10,
        orientation: str = "horizontal",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for stock images"""
        
        try:
            self.logger.info(f"Searching for images: {query}")
            
            # Enhance query with category keywords
            enhanced_query = await self._enhance_search_query(query, category)
            
            # Search both providers
            results = []
            
            # Search Pexels images
            if self.pexels_api_key:
                pexels_results = await self._search_pexels_images(
                    enhanced_query, count // 2 + 1, orientation, **kwargs
                )
                results.extend(pexels_results)
            
            # Search Pixabay images
            if self.pixabay_api_key:
                pixabay_results = await self._search_pixabay_images(
                    enhanced_query, count // 2 + 1, orientation, **kwargs
                )
                results.extend(pixabay_results)
            
            # Filter and sort results
            filtered_results = await self._filter_image_results(results, **kwargs)
            
            # Limit to requested count
            return filtered_results[:count]
            
        except Exception as e:
            self.logger.error(f"Image search failed: {str(e)}")
            return []
    
    async def _enhance_search_query(self, query: str, category: Optional[str]) -> str:
        """Enhance search query with category-specific keywords"""
        
        enhanced_query = query.lower()
        
        if category and category in self.search_categories:
            category_keywords = self.search_categories[category]
            
            # Add relevant keywords that aren't already in the query
            for keyword in category_keywords:
                if keyword not in enhanced_query:
                    enhanced_query += f" {keyword}"
        
        return enhanced_query.strip()
    
    async def _search_pexels_videos(
        self,
        query: str,
        count: int,
        duration_preference: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search Pexels for videos"""
        
        try:
            if not self.pexels_api_key:
                return []
            
            headers = {
                "Authorization": self.pexels_api_key
            }
            
            params = {
                "query": query,
                "per_page": min(count, 80),  # Pexels limit
                "page": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.pexels_video_api_url}/search",
                    headers=headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        videos = data.get("videos", [])
                        
                        results = []
                        for video in videos:
                            result = await self._format_pexels_video(video, duration_preference)
                            if result:
                                results.append(result)
                        
                        self.logger.info(f"Found {len(results)} Pexels videos for '{query}'")
                        return results
                    else:
                        self.logger.warning(f"Pexels API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Pexels video search failed: {str(e)}")
            return []
    
    async def _search_pexels_images(
        self,
        query: str,
        count: int,
        orientation: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search Pexels for images"""
        
        try:
            if not self.pexels_api_key:
                return []
            
            headers = {
                "Authorization": self.pexels_api_key
            }
            
            params = {
                "query": query,
                "per_page": min(count, 80),
                "page": 1,
                "orientation": orientation if orientation in ["landscape", "portrait", "square"] else "landscape"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.pexels_api_url}/search",
                    headers=headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        photos = data.get("photos", [])
                        
                        results = []
                        for photo in photos:
                            result = await self._format_pexels_image(photo)
                            if result:
                                results.append(result)
                        
                        self.logger.info(f"Found {len(results)} Pexels images for '{query}'")
                        return results
                    else:
                        self.logger.warning(f"Pexels API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Pexels image search failed: {str(e)}")
            return []
    
    async def _search_pixabay_videos(
        self,
        query: str,
        count: int,
        duration_preference: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search Pixabay for videos"""
        
        try:
            if not self.pixabay_api_key:
                return []
            
            params = {
                "key": self.pixabay_api_key,
                "q": query,
                "video_type": "film",
                "per_page": min(count, 200),  # Pixabay limit
                "safesearch": "true" if self.content_filters["safe_search"] else "false",
                "min_width": self.content_filters["min_width"],
                "min_height": self.content_filters["min_height"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.pixabay_video_api_url,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        videos = data.get("hits", [])
                        
                        results = []
                        for video in videos:
                            result = await self._format_pixabay_video(video, duration_preference)
                            if result:
                                results.append(result)
                        
                        self.logger.info(f"Found {len(results)} Pixabay videos for '{query}'")
                        return results
                    else:
                        self.logger.warning(f"Pixabay API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Pixabay video search failed: {str(e)}")
            return []
    
    async def _search_pixabay_images(
        self,
        query: str,
        count: int,
        orientation: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search Pixabay for images"""
        
        try:
            if not self.pixabay_api_key:
                return []
            
            params = {
                "key": self.pixabay_api_key,
                "q": query,
                "image_type": "photo",
                "per_page": min(count, 200),
                "safesearch": "true" if self.content_filters["safe_search"] else "false",
                "min_width": self.content_filters["min_width"],
                "min_height": self.content_filters["min_height"]
            }
            
            # Map orientation
            if orientation == "horizontal":
                params["orientation"] = "horizontal"
            elif orientation == "vertical":
                params["orientation"] = "vertical"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.pixabay_api_url,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        images = data.get("hits", [])
                        
                        results = []
                        for image in images:
                            result = await self._format_pixabay_image(image)
                            if result:
                                results.append(result)
                        
                        self.logger.info(f"Found {len(results)} Pixabay images for '{query}'")
                        return results
                    else:
                        self.logger.warning(f"Pixabay API error: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Pixabay image search failed: {str(e)}")
            return []
    
    async def _format_pexels_video(self, video: Dict[str, Any], duration_preference: str) -> Optional[Dict[str, Any]]:
        """Format Pexels video data"""
        
        try:
            video_files = video.get("video_files", [])
            if not video_files:
                return None
            
            # Choose best quality video file
            best_file = None
            for file in video_files:
                if file.get("quality") == "hd":
                    best_file = file
                    break
            
            if not best_file:
                best_file = video_files[0]  # Fallback to first available
            
            return {
                "id": f"pexels_{video['id']}",
                "provider": "pexels",
                "title": f"Pexels Video {video['id']}",
                "description": f"Stock video from Pexels",
                "url": best_file["link"],
                "thumbnail_url": video.get("image", ""),
                "duration": video.get("duration", 0),
                "width": best_file.get("width", 0),
                "height": best_file.get("height", 0),
                "quality": best_file.get("quality", ""),
                "file_type": best_file.get("file_type", "mp4"),
                "photographer": video.get("user", {}).get("name", "Unknown"),
                "photographer_url": video.get("user", {}).get("url", ""),
                "license": "Pexels License (Free for commercial use)"
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to format Pexels video: {str(e)}")
            return None
    
    async def _format_pexels_image(self, photo: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format Pexels image data"""
        
        try:
            src = photo.get("src", {})
            
            return {
                "id": f"pexels_{photo['id']}",
                "provider": "pexels",
                "title": photo.get("alt", f"Pexels Image {photo['id']}"),
                "description": photo.get("alt", "Stock image from Pexels"),
                "url": src.get("large2x", src.get("large", src.get("medium", ""))),
                "thumbnail_url": src.get("medium", src.get("small", "")),
                "width": photo.get("width", 0),
                "height": photo.get("height", 0),
                "photographer": photo.get("photographer", "Unknown"),
                "photographer_url": photo.get("photographer_url", ""),
                "license": "Pexels License (Free for commercial use)",
                "avg_color": photo.get("avg_color", "#000000")
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to format Pexels image: {str(e)}")
            return None
    
    async def _format_pixabay_video(self, video: Dict[str, Any], duration_preference: str) -> Optional[Dict[str, Any]]:
        """Format Pixabay video data"""
        
        try:
            videos = video.get("videos", {})
            
            # Choose appropriate quality
            video_url = ""
            if "large" in videos:
                video_url = videos["large"]["url"]
            elif "medium" in videos:
                video_url = videos["medium"]["url"]
            elif "small" in videos:
                video_url = videos["small"]["url"]
            
            if not video_url:
                return None
            
            return {
                "id": f"pixabay_{video['id']}",
                "provider": "pixabay",
                "title": video.get("tags", f"Pixabay Video {video['id']}"),
                "description": f"Stock video from Pixabay - {video.get('tags', '')}",
                "url": video_url,
                "thumbnail_url": video.get("picture_id", ""),
                "duration": video.get("duration", 0),
                "width": video.get("width", 0),
                "height": video.get("height", 0),
                "views": video.get("views", 0),
                "downloads": video.get("downloads", 0),
                "user": video.get("user", "Unknown"),
                "tags": video.get("tags", ""),
                "license": "Pixabay License (Free for commercial use)"
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to format Pixabay video: {str(e)}")
            return None
    
    async def _format_pixabay_image(self, image: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format Pixabay image data"""
        
        try:
            return {
                "id": f"pixabay_{image['id']}",
                "provider": "pixabay",
                "title": image.get("tags", f"Pixabay Image {image['id']}"),
                "description": f"Stock image from Pixabay - {image.get('tags', '')}",
                "url": image.get("largeImageURL", image.get("webformatURL", "")),
                "thumbnail_url": image.get("previewURL", ""),
                "width": image.get("imageWidth", 0),
                "height": image.get("imageHeight", 0),
                "views": image.get("views", 0),
                "downloads": image.get("downloads", 0),
                "user": image.get("user", "Unknown"),
                "tags": image.get("tags", ""),
                "license": "Pixabay License (Free for commercial use)"
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to format Pixabay image: {str(e)}")
            return None
    
    async def _filter_video_results(self, results: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Filter video results based on criteria"""
        
        filtered = []
        
        for result in results:
            # Duration filter
            duration = result.get("duration", 0)
            if duration < self.content_filters["video_min_duration"]:
                continue
            if duration > self.content_filters["video_max_duration"]:
                continue
            
            # Resolution filter
            width = result.get("width", 0)
            height = result.get("height", 0)
            if width < self.content_filters["min_width"] or height < self.content_filters["min_height"]:
                continue
            
            filtered.append(result)
        
        # Sort by quality/views
        filtered.sort(key=lambda x: (
            x.get("width", 0) * x.get("height", 0),  # Resolution
            x.get("views", 0),  # Popularity
            x.get("downloads", 0)  # Usage
        ), reverse=True)
        
        return filtered
    
    async def _filter_image_results(self, results: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Filter image results based on criteria"""
        
        filtered = []
        
        for result in results:
            # Resolution filter
            width = result.get("width", 0)
            height = result.get("height", 0)
            if width < self.content_filters["min_width"] or height < self.content_filters["min_height"]:
                continue
            
            filtered.append(result)
        
        # Sort by quality/views
        filtered.sort(key=lambda x: (
            x.get("width", 0) * x.get("height", 0),  # Resolution
            x.get("views", 0),  # Popularity
            x.get("downloads", 0)  # Usage
        ), reverse=True)
        
        return filtered
    
    async def download_content(self, content_item: Dict[str, Any]) -> str:
        """Download content item to local cache"""
        
        try:
            content_url = content_item["url"]
            content_id = content_item["id"]
            provider = content_item["provider"]
            
            # Determine file extension
            parsed_url = urlparse(content_url)
            file_ext = Path(parsed_url.path).suffix or ".mp4"
            
            # Create cache filename
            cache_filename = f"{provider}_{content_id}{file_ext}"
            
            # Determine cache directory
            if "video" in content_item.get("file_type", "") or file_ext in [".mp4", ".mov", ".avi"]:
                cache_path = Path(self.videos_cache_dir) / cache_filename
            else:
                cache_path = Path(self.images_cache_dir) / cache_filename
            
            # Check if already cached
            if cache_path.exists():
                self.logger.info(f"Content already cached: {cache_path}")
                return str(cache_path)
            
            # Download content
            self.logger.info(f"Downloading content: {content_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(content_url) as response:
                    if response.status == 200:
                        cache_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(cache_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        self.logger.info(f"Content downloaded: {cache_path}")
                        return str(cache_path)
                    else:
                        raise RuntimeError(f"Download failed: HTTP {response.status}")
            
        except Exception as e:
            self.logger.error(f"Content download failed: {str(e)}")
            raise
    
    async def get_b_roll_content(
        self,
        topic: str,
        num_videos: int = 3,
        num_images: int = 5,
        category: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get B-roll content for a topic"""
        
        try:
            # Search for videos and images
            videos = await self.search_videos(
                query=topic,
                category=category,
                count=num_videos,
                duration_preference="short"
            )
            
            images = await self.search_images(
                query=topic,
                category=category,
                count=num_images,
                orientation="horizontal"
            )
            
            return {
                "videos": videos,
                "images": images,
                "topic": topic,
                "category": category,
                "total_items": len(videos) + len(images)
            }
            
        except Exception as e:
            self.logger.error(f"B-roll content search failed: {str(e)}")
            return {"videos": [], "images": [], "topic": topic, "category": category, "total_items": 0}
    
    def get_available_categories(self) -> List[str]:
        """Get available search categories"""
        return list(self.search_categories.keys())
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API availability status"""
        return {
            "pexels_available": bool(self.pexels_api_key),
            "pixabay_available": bool(self.pixabay_api_key),
            "cache_size": self._get_cache_size(),
            "available_categories": len(self.search_categories)
        }
    
    def _get_cache_size(self) -> Dict[str, str]:
        """Get cache directory sizes"""
        try:
            def get_dir_size(directory):
                if not Path(directory).exists():
                    return 0
                return sum(f.stat().st_size for f in Path(directory).rglob('*') if f.is_file())
            
            videos_size = get_dir_size(self.videos_cache_dir)
            images_size = get_dir_size(self.images_cache_dir)
            total_size = videos_size + images_size
            
            def format_size(size):
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"
            
            return {
                "videos": format_size(videos_size),
                "images": format_size(images_size),
                "total": format_size(total_size)
            }
            
        except Exception:
            return {"videos": "Unknown", "images": "Unknown", "total": "Unknown"}