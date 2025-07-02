"""
Scene Controller
Handles dynamic scene switching, overlay management, and visual automation
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..base import BaseModule

logger = logging.getLogger(__name__)

class SceneTransition(Enum):
    """Scene transition types"""
    CUT = "Cut"
    FADE = "Fade"
    SLIDE = "Slide"
    STINGER = "Stinger"
    WIPE = "Wipe"

@dataclass
class SceneItem:
    """Scene item configuration"""
    name: str
    source_name: str
    visible: bool = True
    position: Tuple[float, float] = (0, 0)
    scale: Tuple[float, float] = (1.0, 1.0)
    rotation: float = 0
    opacity: float = 100
    crop: Dict[str, int] = field(default_factory=dict)
    filters: List[str] = field(default_factory=list)

@dataclass
class Scene:
    """Scene configuration"""
    name: str
    items: List[SceneItem] = field(default_factory=list)
    transition: SceneTransition = SceneTransition.FADE
    transition_duration: int = 300  # milliseconds
    auto_switch_after: Optional[int] = None  # seconds
    next_scene: Optional[str] = None
    triggers: List[str] = field(default_factory=list)  # Event triggers

@dataclass
class OverlayElement:
    """Overlay element configuration"""
    name: str
    type: str  # text, image, browser_source, etc.
    source_name: str
    content: Any = None
    position: Tuple[float, float] = (0, 0)
    size: Tuple[float, float] = (100, 50)
    visible: bool = True
    animation: Optional[str] = None
    auto_hide_after: Optional[int] = None
    update_frequency: Optional[int] = None  # seconds

class SceneController(BaseModule):
    """Advanced scene and overlay management"""
    
    def __init__(self, livestream_manager=None):
        super().__init__()
        self.module_name = "scene_controller"
        self.livestream_manager = livestream_manager
        
        # Scene management
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[str] = None
        self.scene_history: List[Tuple[str, datetime]] = []
        self.scene_timers: Dict[str, asyncio.Task] = {}
        
        # Overlay management
        self.overlay_elements: Dict[str, OverlayElement] = {}
        self.active_overlays: Dict[str, bool] = {}
        self.overlay_update_tasks: Dict[str, asyncio.Task] = {}
        
        # Transition settings
        self.default_transition = SceneTransition.FADE
        self.default_transition_duration = 500
        
        # Auto-switch rules
        self.auto_switch_rules = {
            "viewer_count_threshold": {
                "low_viewers": {"threshold": 5, "scene": "waiting_for_viewers"},
                "high_viewers": {"threshold": 100, "scene": "main_with_chat"}
            },
            "time_based": {
                "intro_duration": 30,
                "break_duration": 300,
                "outro_duration": 60
            },
            "event_triggered": {
                "new_follower": {"scene": "celebration", "duration": 10},
                "donation": {"scene": "thank_you", "duration": 15},
                "raid": {"scene": "raid_celebration", "duration": 30}
            }
        }
        
        # Pre-defined scene templates
        self._setup_default_scenes()
        self._setup_default_overlays()
    
    async def _setup_module(self):
        """Initialize scene controller"""
        await super()._setup_module()
        
        try:
            # Initialize overlay update tasks
            await self._start_overlay_updates()
            
            self.logger.info("Scene Controller initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scene controller: {str(e)}")
            raise
    
    def _setup_default_scenes(self):
        """Setup default scene configurations"""
        # Starting/Intro Scene
        self.scenes["intro"] = Scene(
            name="intro",
            items=[
                SceneItem("webcam", "Webcam", position=(100, 100)),
                SceneItem("intro_overlay", "Intro Overlay"),
                SceneItem("starting_soon", "Starting Soon Text"),
                SceneItem("social_media", "Social Media Links", position=(50, 400))
            ],
            transition=SceneTransition.FADE,
            auto_switch_after=30,
            next_scene="main"
        )
        
        # Main streaming scene
        self.scenes["main"] = Scene(
            name="main",
            items=[
                SceneItem("webcam", "Webcam", position=(50, 50)),
                SceneItem("screen_capture", "Screen Capture", position=(300, 50)),
                SceneItem("chat_overlay", "Chat Overlay", position=(800, 100)),
                SceneItem("recent_follower", "Recent Follower", position=(50, 400)),
                SceneItem("subscriber_count", "Subscriber Count", position=(50, 450))
            ],
            transition=SceneTransition.FADE
        )
        
        # Break scene
        self.scenes["break"] = Scene(
            name="break",
            items=[
                SceneItem("break_screen", "Break Screen"),
                SceneItem("break_timer", "Break Timer", position=(400, 300)),
                SceneItem("music_info", "Now Playing", position=(50, 450)),
                SceneItem("social_links", "Social Links", position=(50, 500))
            ],
            transition=SceneTransition.SLIDE,
            auto_switch_after=300,
            next_scene="main"
        )
        
        # Celebration scene (for follows, donations, etc.)
        self.scenes["celebration"] = Scene(
            name="celebration",
            items=[
                SceneItem("webcam", "Webcam", position=(100, 100)),
                SceneItem("celebration_overlay", "Celebration Overlay"),
                SceneItem("confetti_effect", "Confetti Effect"),
                SceneItem("thank_you_text", "Thank You Text", position=(200, 200))
            ],
            transition=SceneTransition.STINGER,
            auto_switch_after=10,
            next_scene="main"
        )
        
        # Outro scene
        self.scenes["outro"] = Scene(
            name="outro",
            items=[
                SceneItem("webcam", "Webcam", position=(100, 100)),
                SceneItem("outro_overlay", "Outro Overlay"),
                SceneItem("social_links", "Social Links", position=(200, 300)),
                SceneItem("subscribe_reminder", "Subscribe Reminder", position=(200, 350))
            ],
            transition=SceneTransition.FADE,
            auto_switch_after=60,
            next_scene=None  # End stream
        )
    
    def _setup_default_overlays(self):
        """Setup default overlay elements"""
        # Chat overlay
        self.overlay_elements["chat"] = OverlayElement(
            name="chat",
            type="browser_source",
            source_name="Chat Overlay",
            position=(800, 100),
            size=(400, 600),
            update_frequency=5
        )
        
        # Recent follower
        self.overlay_elements["recent_follower"] = OverlayElement(
            name="recent_follower",
            type="text",
            source_name="Recent Follower",
            content="Welcome new follower!",
            position=(50, 400),
            size=(300, 30),
            animation="slide_in",
            auto_hide_after=10
        )
        
        # Subscriber count
        self.overlay_elements["subscriber_count"] = OverlayElement(
            name="subscriber_count",
            type="text",
            source_name="Subscriber Count",
            content="Subscribers: 0",
            position=(50, 450),
            size=(200, 30),
            update_frequency=60
        )
        
        # Donation alert
        self.overlay_elements["donation_alert"] = OverlayElement(
            name="donation_alert",
            type="browser_source",
            source_name="Donation Alert",
            position=(400, 200),
            size=(400, 200),
            visible=False,
            animation="bounce_in",
            auto_hide_after=15
        )
        
        # Stream timer
        self.overlay_elements["stream_timer"] = OverlayElement(
            name="stream_timer",
            type="text",
            source_name="Stream Timer",
            content="Stream Time: 00:00:00",
            position=(700, 50),
            size=(200, 30),
            update_frequency=1
        )
    
    async def _start_overlay_updates(self):
        """Start automatic overlay update tasks"""
        for name, overlay in self.overlay_elements.items():
            if overlay.update_frequency:
                task = asyncio.create_task(
                    self._update_overlay_loop(name, overlay.update_frequency)
                )
                self.overlay_update_tasks[name] = task
    
    async def _update_overlay_loop(self, overlay_name: str, frequency: int):
        """Continuously update overlay element"""
        while True:
            try:
                await self.update_overlay_content(overlay_name)
                await asyncio.sleep(frequency)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error updating overlay {overlay_name}: {str(e)}")
                await asyncio.sleep(frequency)
    
    async def switch_scene(
        self,
        scene_name: str,
        transition: Optional[SceneTransition] = None,
        transition_duration: Optional[int] = None
    ) -> bool:
        """Switch to specified scene with transition"""
        try:
            if scene_name not in self.scenes:
                self.logger.error(f"Scene {scene_name} not found")
                return False
            
            scene = self.scenes[scene_name]
            
            # Use scene-specific or provided transition settings
            trans = transition or scene.transition or self.default_transition
            duration = transition_duration or scene.transition_duration or self.default_transition_duration
            
            # Set transition
            if self.livestream_manager:
                await self._set_transition(trans, duration)
                
                # Switch scene
                success = await self.livestream_manager.switch_scene(scene_name)
                
                if success:
                    # Update current scene
                    old_scene = self.current_scene
                    self.current_scene = scene_name
                    
                    # Add to history
                    self.scene_history.append((scene_name, datetime.utcnow()))
                    
                    # Cancel old scene timer
                    if old_scene and old_scene in self.scene_timers:
                        self.scene_timers[old_scene].cancel()
                        del self.scene_timers[old_scene]
                    
                    # Setup auto-switch timer
                    if scene.auto_switch_after and scene.next_scene:
                        timer_task = asyncio.create_task(
                            self._auto_switch_timer(scene.auto_switch_after, scene.next_scene)
                        )
                        self.scene_timers[scene_name] = timer_task
                    
                    # Apply scene configuration
                    await self._apply_scene_configuration(scene)
                    
                    await self.log_activity("scene_switched", {
                        "from_scene": old_scene,
                        "to_scene": scene_name,
                        "transition": trans.value,
                        "duration": duration
                    })
                    
                    self.logger.info(f"Switched to scene: {scene_name}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error switching scene: {str(e)}")
            return False
    
    async def _set_transition(self, transition: SceneTransition, duration: int):
        """Set OBS transition"""
        try:
            if not self.livestream_manager:
                return
            
            # Set transition type
            await self.livestream_manager._send_obs_request("SetCurrentSceneTransition", {
                "transitionName": transition.value
            })
            
            # Set transition duration
            await self.livestream_manager._send_obs_request("SetCurrentSceneTransitionDuration", {
                "transitionDuration": duration
            })
            
        except Exception as e:
            self.logger.error(f"Error setting transition: {str(e)}")
    
    async def _auto_switch_timer(self, delay: int, next_scene: str):
        """Auto-switch timer for scene transitions"""
        try:
            await asyncio.sleep(delay)
            await self.switch_scene(next_scene)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Error in auto-switch timer: {str(e)}")
    
    async def _apply_scene_configuration(self, scene: Scene):
        """Apply scene item configurations"""
        try:
            for item in scene.items:
                # Update item visibility
                if self.livestream_manager:
                    await self._set_scene_item_enabled(scene.name, item.name, item.visible)
                    
                    # Update item transform
                    if item.position != (0, 0) or item.scale != (1.0, 1.0):
                        await self._set_scene_item_transform(scene.name, item.name, {
                            "positionX": item.position[0],
                            "positionY": item.position[1],
                            "scaleX": item.scale[0],
                            "scaleY": item.scale[1],
                            "rotation": item.rotation
                        })
            
        except Exception as e:
            self.logger.error(f"Error applying scene configuration: {str(e)}")
    
    async def _set_scene_item_enabled(self, scene_name: str, item_name: str, enabled: bool):
        """Set scene item visibility"""
        try:
            if self.livestream_manager:
                await self.livestream_manager._send_obs_request("SetSceneItemEnabled", {
                    "sceneName": scene_name,
                    "sceneItemId": item_name,  # This should be the actual item ID
                    "sceneItemEnabled": enabled
                })
        except Exception as e:
            self.logger.error(f"Error setting scene item enabled: {str(e)}")
    
    async def _set_scene_item_transform(self, scene_name: str, item_name: str, transform: Dict[str, Any]):
        """Set scene item transform properties"""
        try:
            if self.livestream_manager:
                await self.livestream_manager._send_obs_request("SetSceneItemTransform", {
                    "sceneName": scene_name,
                    "sceneItemId": item_name,  # This should be the actual item ID
                    "sceneItemTransform": transform
                })
        except Exception as e:
            self.logger.error(f"Error setting scene item transform: {str(e)}")
    
    async def show_overlay(self, overlay_name: str, duration: Optional[int] = None) -> bool:
        """Show overlay element"""
        try:
            if overlay_name not in self.overlay_elements:
                self.logger.error(f"Overlay {overlay_name} not found")
                return False
            
            overlay = self.overlay_elements[overlay_name]
            
            # Set overlay visible
            if self.livestream_manager:
                await self._set_source_visibility(overlay.source_name, True)
            
            self.active_overlays[overlay_name] = True
            
            # Auto-hide timer
            hide_duration = duration or overlay.auto_hide_after
            if hide_duration:
                asyncio.create_task(self._auto_hide_overlay(overlay_name, hide_duration))
            
            # Apply animation
            if overlay.animation:
                await self._apply_overlay_animation(overlay_name, overlay.animation)
            
            self.logger.info(f"Showed overlay: {overlay_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error showing overlay: {str(e)}")
            return False
    
    async def hide_overlay(self, overlay_name: str) -> bool:
        """Hide overlay element"""
        try:
            if overlay_name not in self.overlay_elements:
                return False
            
            overlay = self.overlay_elements[overlay_name]
            
            # Set overlay invisible
            if self.livestream_manager:
                await self._set_source_visibility(overlay.source_name, False)
            
            self.active_overlays[overlay_name] = False
            
            self.logger.info(f"Hid overlay: {overlay_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error hiding overlay: {str(e)}")
            return False
    
    async def _auto_hide_overlay(self, overlay_name: str, delay: int):
        """Auto-hide overlay after delay"""
        try:
            await asyncio.sleep(delay)
            await self.hide_overlay(overlay_name)
        except Exception as e:
            self.logger.error(f"Error in auto-hide overlay: {str(e)}")
    
    async def _set_source_visibility(self, source_name: str, visible: bool):
        """Set source visibility in current scene"""
        try:
            if self.livestream_manager and self.current_scene:
                await self.livestream_manager._send_obs_request("SetSceneItemEnabled", {
                    "sceneName": self.current_scene,
                    "sceneItemId": source_name,  # This should be the actual item ID
                    "sceneItemEnabled": visible
                })
        except Exception as e:
            self.logger.error(f"Error setting source visibility: {str(e)}")
    
    async def _apply_overlay_animation(self, overlay_name: str, animation: str):
        """Apply animation to overlay element"""
        try:
            # This would implement various animation effects
            # For now, we'll just log the animation
            self.logger.info(f"Applied {animation} animation to {overlay_name}")
            
            # Implement specific animations
            if animation == "slide_in":
                await self._animate_slide_in(overlay_name)
            elif animation == "bounce_in":
                await self._animate_bounce_in(overlay_name)
            elif animation == "fade_in":
                await self._animate_fade_in(overlay_name)
                
        except Exception as e:
            self.logger.error(f"Error applying animation: {str(e)}")
    
    async def _animate_slide_in(self, overlay_name: str):
        """Slide in animation"""
        # Implementation would depend on OBS filter capabilities
        pass
    
    async def _animate_bounce_in(self, overlay_name: str):
        """Bounce in animation"""
        # Implementation would depend on OBS filter capabilities
        pass
    
    async def _animate_fade_in(self, overlay_name: str):
        """Fade in animation"""
        # Implementation would depend on OBS filter capabilities
        pass
    
    async def update_overlay_content(self, overlay_name: str, content: Any = None):
        """Update overlay element content"""
        try:
            if overlay_name not in self.overlay_elements:
                return
            
            overlay = self.overlay_elements[overlay_name]
            
            # Generate dynamic content if not provided
            if content is None:
                content = await self._generate_overlay_content(overlay_name)
            
            # Update content based on overlay type
            if overlay.type == "text":
                await self._update_text_source(overlay.source_name, content)
            elif overlay.type == "browser_source":
                await self._update_browser_source(overlay.source_name, content)
            
            overlay.content = content
            
        except Exception as e:
            self.logger.error(f"Error updating overlay content: {str(e)}")
    
    async def _generate_overlay_content(self, overlay_name: str) -> str:
        """Generate dynamic content for overlay"""
        try:
            if overlay_name == "subscriber_count":
                # This would fetch real subscriber count
                return "Subscribers: 1,234"
            elif overlay_name == "stream_timer":
                # Calculate stream duration
                return f"Stream Time: {datetime.utcnow().strftime('%H:%M:%S')}"
            elif overlay_name == "recent_follower":
                # This would fetch recent follower
                return "Welcome, NewFollower123!"
            else:
                return "Dynamic Content"
                
        except Exception as e:
            self.logger.error(f"Error generating overlay content: {str(e)}")
            return ""
    
    async def _update_text_source(self, source_name: str, text: str):
        """Update text source content"""
        try:
            if self.livestream_manager:
                await self.livestream_manager._send_obs_request("SetInputSettings", {
                    "inputName": source_name,
                    "inputSettings": {
                        "text": text
                    }
                })
        except Exception as e:
            self.logger.error(f"Error updating text source: {str(e)}")
    
    async def _update_browser_source(self, source_name: str, url: str):
        """Update browser source URL"""
        try:
            if self.livestream_manager:
                await self.livestream_manager._send_obs_request("SetInputSettings", {
                    "inputName": source_name,
                    "inputSettings": {
                        "url": url
                    }
                })
        except Exception as e:
            self.logger.error(f"Error updating browser source: {str(e)}")
    
    async def trigger_event_scene(self, event_type: str, data: Dict[str, Any] = None):
        """Trigger scene change based on event"""
        try:
            event_config = self.auto_switch_rules.get("event_triggered", {}).get(event_type)
            
            if event_config:
                scene_name = event_config["scene"]
                duration = event_config.get("duration")
                
                if scene_name in self.scenes:
                    # Store current scene to return to
                    previous_scene = self.current_scene
                    
                    # Switch to event scene
                    await self.switch_scene(scene_name)
                    
                    # Auto-return to previous scene
                    if duration and previous_scene:
                        asyncio.create_task(
                            self._return_to_scene(duration, previous_scene)
                        )
                    
                    await self.log_activity("event_scene_triggered", {
                        "event_type": event_type,
                        "scene": scene_name,
                        "duration": duration,
                        "data": data
                    })
                    
        except Exception as e:
            self.logger.error(f"Error triggering event scene: {str(e)}")
    
    async def _return_to_scene(self, delay: int, scene_name: str):
        """Return to specified scene after delay"""
        try:
            await asyncio.sleep(delay)
            await self.switch_scene(scene_name)
        except Exception as e:
            self.logger.error(f"Error returning to scene: {str(e)}")
    
    async def create_scene(self, scene_name: str, scene_config: Dict[str, Any]) -> bool:
        """Create new scene configuration"""
        try:
            # Parse scene configuration
            items = []
            for item_config in scene_config.get("items", []):
                item = SceneItem(
                    name=item_config["name"],
                    source_name=item_config["source_name"],
                    visible=item_config.get("visible", True),
                    position=tuple(item_config.get("position", [0, 0])),
                    scale=tuple(item_config.get("scale", [1.0, 1.0])),
                    rotation=item_config.get("rotation", 0),
                    opacity=item_config.get("opacity", 100)
                )
                items.append(item)
            
            # Create scene
            scene = Scene(
                name=scene_name,
                items=items,
                transition=SceneTransition(scene_config.get("transition", "Fade")),
                transition_duration=scene_config.get("transition_duration", 500),
                auto_switch_after=scene_config.get("auto_switch_after"),
                next_scene=scene_config.get("next_scene")
            )
            
            self.scenes[scene_name] = scene
            
            self.logger.info(f"Created scene: {scene_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating scene: {str(e)}")
            return False
    
    async def create_overlay(self, overlay_name: str, overlay_config: Dict[str, Any]) -> bool:
        """Create new overlay element"""
        try:
            overlay = OverlayElement(
                name=overlay_name,
                type=overlay_config["type"],
                source_name=overlay_config["source_name"],
                content=overlay_config.get("content"),
                position=tuple(overlay_config.get("position", [0, 0])),
                size=tuple(overlay_config.get("size", [100, 50])),
                visible=overlay_config.get("visible", True),
                animation=overlay_config.get("animation"),
                auto_hide_after=overlay_config.get("auto_hide_after"),
                update_frequency=overlay_config.get("update_frequency")
            )
            
            self.overlay_elements[overlay_name] = overlay
            
            # Start update task if needed
            if overlay.update_frequency:
                task = asyncio.create_task(
                    self._update_overlay_loop(overlay_name, overlay.update_frequency)
                )
                self.overlay_update_tasks[overlay_name] = task
            
            self.logger.info(f"Created overlay: {overlay_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating overlay: {str(e)}")
            return False
    
    def get_scenes(self) -> Dict[str, Dict[str, Any]]:
        """Get all scene configurations"""
        return {
            name: {
                "name": scene.name,
                "items": [
                    {
                        "name": item.name,
                        "source_name": item.source_name,
                        "visible": item.visible,
                        "position": item.position,
                        "scale": item.scale,
                        "rotation": item.rotation,
                        "opacity": item.opacity
                    }
                    for item in scene.items
                ],
                "transition": scene.transition.value,
                "transition_duration": scene.transition_duration,
                "auto_switch_after": scene.auto_switch_after,
                "next_scene": scene.next_scene
            }
            for name, scene in self.scenes.items()
        }
    
    def get_overlays(self) -> Dict[str, Dict[str, Any]]:
        """Get all overlay configurations"""
        return {
            name: {
                "name": overlay.name,
                "type": overlay.type,
                "source_name": overlay.source_name,
                "content": overlay.content,
                "position": overlay.position,
                "size": overlay.size,
                "visible": overlay.visible,
                "animation": overlay.animation,
                "auto_hide_after": overlay.auto_hide_after,
                "update_frequency": overlay.update_frequency,
                "active": self.active_overlays.get(name, False)
            }
            for name, overlay in self.overlay_elements.items()
        }
    
    def get_scene_history(self) -> List[Dict[str, Any]]:
        """Get scene switch history"""
        return [
            {
                "scene": scene,
                "timestamp": timestamp.isoformat(),
                "duration": (datetime.utcnow() - timestamp).total_seconds()
            }
            for scene, timestamp in self.scene_history[-10:]  # Last 10 switches
        ]
    
    def get_controller_stats(self) -> Dict[str, Any]:
        """Get scene controller statistics"""
        stats = super().get_status()
        stats.update({
            "total_scenes": len(self.scenes),
            "total_overlays": len(self.overlay_elements),
            "current_scene": self.current_scene,
            "active_overlays": len([name for name, active in self.active_overlays.items() if active]),
            "running_timers": len(self.scene_timers),
            "update_tasks": len(self.overlay_update_tasks),
            "scene_switches": len(self.scene_history),
            "connected_to_obs": self.livestream_manager is not None and getattr(self.livestream_manager, 'obs_connection', {}).get('connected', False)
        })
        return stats