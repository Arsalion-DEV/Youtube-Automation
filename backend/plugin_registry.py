"""
Plugin Registry System for YouTube Automation Platform
Manages 3rd-party AI plugins and extensions
"""

import os
import json
import importlib.util
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import inspect
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PluginInfo:
    """Plugin information structure"""
    name: str
    version: str
    description: str
    author: str
    category: str
    dependencies: List[str]
    hooks: List[str]
    enabled: bool = True
    installed_at: str = ""
    file_path: str = ""
    checksum: str = ""

class PluginHook:
    """Plugin hook decorator and manager"""
    
    _hooks: Dict[str, List[Callable]] = {}
    
    @classmethod
    def register(cls, hook_name: str):
        """Decorator to register plugin hooks"""
        def decorator(func: Callable):
            if hook_name not in cls._hooks:
                cls._hooks[hook_name] = []
            cls._hooks[hook_name].append(func)
            logger.info(f"Registered hook '{hook_name}' for function '{func.__name__}'")
            return func
        return decorator
    
    @classmethod
    def execute(cls, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute all functions registered to a hook"""
        results = []
        if hook_name in cls._hooks:
            for func in cls._hooks[hook_name]:
                try:
                    result = func(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error executing hook '{hook_name}' function '{func.__name__}': {str(e)}")
        return results
    
    @classmethod
    def get_hooks(cls) -> Dict[str, int]:
        """Get all registered hooks and their function counts"""
        return {hook: len(funcs) for hook, funcs in cls._hooks.items()}

class PluginRegistry:
    """Main plugin registry and management system"""
    
    def __init__(self, plugins_dir: str = "plugins", config_file: str = "plugin_config.json"):
        self.plugins_dir = Path(plugins_dir)
        self.config_file = Path(config_file)
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_modules = {}
        
        # Create plugins directory if it doesn't exist
        self.plugins_dir.mkdir(exist_ok=True)
        
        # Initialize available hooks
        self.available_hooks = {
            # Video Generation Hooks
            "before_script_generation": "Called before script generation",
            "after_script_generation": "Called after script generation with script data",
            "before_image_generation": "Called before image generation",
            "after_image_generation": "Called after image generation with image paths",
            "before_video_generation": "Called before video generation",
            "after_video_generation": "Called after video generation with video path",
            "before_voice_synthesis": "Called before voice synthesis",
            "after_voice_synthesis": "Called after voice synthesis with audio path",
            
            # Channel Management Hooks
            "before_video_upload": "Called before uploading video to YouTube",
            "after_video_upload": "Called after successful video upload",
            "before_metadata_generation": "Called before generating video metadata",
            "after_metadata_generation": "Called after generating metadata",
            
            # Engagement Hooks
            "before_comment_reply": "Called before replying to comments",
            "after_comment_reply": "Called after replying to comments",
            "before_community_post": "Called before creating community post",
            "after_community_post": "Called after creating community post",
            
            # Analytics Hooks
            "before_analytics_fetch": "Called before fetching analytics",
            "after_analytics_fetch": "Called after fetching analytics data",
            "on_performance_threshold": "Called when performance metrics meet thresholds",
            
            # Monetization Hooks
            "before_supporter_content": "Called before generating supporter content",
            "after_supporter_content": "Called after generating supporter content",
            "on_new_supporter": "Called when new supporter is detected",
            
            # Custom Hooks
            "custom_ai_model": "Hook for custom AI model integration",
            "custom_voice_model": "Hook for custom voice model integration",
            "custom_video_effect": "Hook for custom video effects",
            "custom_analytics_widget": "Hook for custom analytics widgets",
        }
        
        logger.info(f"Plugin registry initialized with {len(self.available_hooks)} available hooks")
    
    def load_config(self) -> Dict[str, Any]:
        """Load plugin configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading plugin config: {str(e)}")
                return {}
        return {}
    
    def save_config(self):
        """Save plugin configuration"""
        try:
            config = {
                "plugins": {name: asdict(plugin) for name, plugin in self.plugins.items()},
                "last_updated": datetime.utcnow().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving plugin config: {str(e)}")
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum for integrity verification"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {str(e)}")
            return ""
    
    def validate_plugin(self, plugin_path: Path) -> Optional[PluginInfo]:
        """Validate plugin structure and extract metadata"""
        try:
            # Load plugin module
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            if not spec or not spec.loader:
                raise ValueError("Invalid plugin file")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for required plugin metadata
            if not hasattr(module, 'PLUGIN_INFO'):
                raise ValueError("Plugin missing PLUGIN_INFO")
            
            plugin_info_dict = module.PLUGIN_INFO
            required_fields = ['name', 'version', 'description', 'author', 'category']
            
            for field in required_fields:
                if field not in plugin_info_dict:
                    raise ValueError(f"Plugin missing required field: {field}")
            
            # Extract hooks used by plugin
            hooks_used = []
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, '_plugin_hooks'):
                    hooks_used.extend(obj._plugin_hooks)
            
            # Create PluginInfo
            plugin_info = PluginInfo(
                name=plugin_info_dict['name'],
                version=plugin_info_dict['version'],
                description=plugin_info_dict['description'],
                author=plugin_info_dict['author'],
                category=plugin_info_dict['category'],
                dependencies=plugin_info_dict.get('dependencies', []),
                hooks=hooks_used,
                file_path=str(plugin_path),
                checksum=self.calculate_checksum(plugin_path),
                installed_at=datetime.utcnow().isoformat()
            )
            
            return plugin_info
            
        except Exception as e:
            logger.error(f"Plugin validation failed for {plugin_path}: {str(e)}")
            return None
    
    def install_plugin(self, plugin_source: str) -> bool:
        """Install plugin from file path or URL"""
        try:
            if plugin_source.startswith(('http://', 'https://')):
                # Download plugin from URL
                import requests
                response = requests.get(plugin_source)
                response.raise_for_status()
                
                # Generate filename from URL
                filename = plugin_source.split('/')[-1]
                if not filename.endswith('.py'):
                    filename += '.py'
                
                plugin_path = self.plugins_dir / filename
                with open(plugin_path, 'wb') as f:
                    f.write(response.content)
            else:
                # Local file installation
                source_path = Path(plugin_source)
                if not source_path.exists():
                    raise FileNotFoundError(f"Plugin file not found: {plugin_source}")
                
                plugin_path = self.plugins_dir / source_path.name
                import shutil
                shutil.copy2(source_path, plugin_path)
            
            # Validate and register plugin
            plugin_info = self.validate_plugin(plugin_path)
            if not plugin_info:
                # Remove failed installation
                plugin_path.unlink(missing_ok=True)
                return False
            
            # Check for conflicts
            if plugin_info.name in self.plugins:
                logger.warning(f"Plugin '{plugin_info.name}' already exists, updating...")
            
            self.plugins[plugin_info.name] = plugin_info
            self.save_config()
            
            logger.info(f"Plugin '{plugin_info.name}' installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Plugin installation failed: {str(e)}")
            return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall plugin"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"Plugin '{plugin_name}' not found")
            
            plugin_info = self.plugins[plugin_name]
            plugin_path = Path(plugin_info.file_path)
            
            # Remove from loaded modules
            if plugin_name in self.loaded_modules:
                del self.loaded_modules[plugin_name]
            
            # Remove file
            plugin_path.unlink(missing_ok=True)
            
            # Remove from registry
            del self.plugins[plugin_name]
            self.save_config()
            
            logger.info(f"Plugin '{plugin_name}' uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Plugin uninstallation failed: {str(e)}")
            return False
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        try:
            if plugin_name not in self.plugins:
                raise ValueError(f"Plugin '{plugin_name}' not found")
            
            plugin_info = self.plugins[plugin_name]
            if not plugin_info.enabled:
                logger.info(f"Plugin '{plugin_name}' is disabled")
                return False
            
            plugin_path = Path(plugin_info.file_path)
            if not plugin_path.exists():
                raise FileNotFoundError(f"Plugin file not found: {plugin_path}")
            
            # Verify checksum
            current_checksum = self.calculate_checksum(plugin_path)
            if current_checksum != plugin_info.checksum:
                logger.warning(f"Plugin '{plugin_name}' checksum mismatch, file may have been modified")
            
            # Load plugin module
            spec = importlib.util.spec_from_file_location(f"plugin_{plugin_name}", plugin_path)
            if not spec or not spec.loader:
                raise ValueError("Invalid plugin file")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Store loaded module
            self.loaded_modules[plugin_name] = module
            
            # Call plugin initialization if available
            if hasattr(module, 'plugin_init'):
                module.plugin_init()
            
            logger.info(f"Plugin '{plugin_name}' loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Plugin loading failed for '{plugin_name}': {str(e)}")
            return False
    
    def load_plugins(self):
        """Load all enabled plugins"""
        logger.info("Loading plugins...")
        
        # Load configuration
        config = self.load_config()
        if 'plugins' in config:
            for name, plugin_data in config['plugins'].items():
                try:
                    self.plugins[name] = PluginInfo(**plugin_data)
                except Exception as e:
                    logger.error(f"Error loading plugin config for '{name}': {str(e)}")
        
        # Scan plugins directory for new plugins
        for plugin_file in self.plugins_dir.glob("*.py"):
            plugin_name = plugin_file.stem
            if plugin_name not in self.plugins:
                plugin_info = self.validate_plugin(plugin_file)
                if plugin_info:
                    self.plugins[plugin_name] = plugin_info
                    logger.info(f"Discovered new plugin: {plugin_name}")
        
        # Load enabled plugins
        loaded_count = 0
        for plugin_name in self.plugins:
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        self.save_config()
        logger.info(f"Loaded {loaded_count}/{len(self.plugins)} plugins")
    
    def get_plugins(self) -> List[PluginInfo]:
        """Get all registered plugins"""
        return list(self.plugins.values())
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get specific plugin info"""
        return self.plugins.get(plugin_name)
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self.save_config()
            return self.load_plugin(plugin_name)
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            if plugin_name in self.loaded_modules:
                # Call plugin cleanup if available
                module = self.loaded_modules[plugin_name]
                if hasattr(module, 'plugin_cleanup'):
                    try:
                        module.plugin_cleanup()
                    except Exception as e:
                        logger.error(f"Error during plugin cleanup for '{plugin_name}': {str(e)}")
                del self.loaded_modules[plugin_name]
            self.save_config()
            return True
        return False
    
    def get_available_hooks(self) -> Dict[str, str]:
        """Get all available hooks"""
        return self.available_hooks
    
    def get_active_hooks(self) -> Dict[str, int]:
        """Get currently active hooks"""
        return PluginHook.get_hooks()
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute a plugin hook"""
        return PluginHook.execute(hook_name, *args, **kwargs)

# Global plugin registry instance
plugin_registry = PluginRegistry()

# Hook decorator for easy plugin development
hook = PluginHook.register