"""
Plugin Registry Manager
Handles plugin discovery, registration, and management
"""

import json
import os
import hashlib
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import requests
import semver
from ..database import DatabaseManager

class PluginRegistryManager:
    def __init__(self, db_manager: DatabaseManager, plugins_dir: str = "plugins"):
        self.db = db_manager
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        self.registry_cache = {}
        self.init_registry_tables()
        
    def init_registry_tables(self):
        """Initialize plugin registry database tables"""
        with self.db.get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_registry (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    author TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    tags TEXT,
                    manifest TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    size_bytes INTEGER,
                    downloads INTEGER DEFAULT 0,
                    rating REAL DEFAULT 0.0,
                    rating_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    is_featured BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_dependencies (
                    plugin_id TEXT,
                    dependency_name TEXT,
                    dependency_version TEXT,
                    is_optional BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (plugin_id) REFERENCES plugin_registry (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_installations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT,
                    user_id TEXT,
                    version TEXT,
                    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    config TEXT,
                    FOREIGN KEY (plugin_id) REFERENCES plugin_registry (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT,
                    user_id TEXT,
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    review_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plugin_id) REFERENCES plugin_registry (id)
                )
            """)
    
    def register_plugin(self, plugin_file: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new plugin in the marketplace"""
        try:
            # Validate manifest
            required_fields = ['id', 'name', 'version', 'author', 'category', 'entry_point']
            for field in required_fields:
                if field not in manifest:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Check if plugin already exists
            existing = self.get_plugin(manifest['id'])
            if existing and semver.compare(existing['version'], manifest['version']) >= 0:
                return {"success": False, "error": "Plugin version already exists or is older"}
            
            # Calculate file hash
            with open(plugin_file, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            file_size = os.path.getsize(plugin_file)
            
            with self.db.get_db() as conn:
                # Insert or update plugin
                conn.execute("""
                    INSERT OR REPLACE INTO plugin_registry 
                    (id, name, version, author, description, category, tags, manifest, 
                     file_hash, size_bytes, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
                """, (
                    manifest['id'],
                    manifest['name'], 
                    manifest['version'],
                    manifest['author'],
                    manifest.get('description', ''),
                    manifest['category'],
                    json.dumps(manifest.get('tags', [])),
                    json.dumps(manifest),
                    file_hash,
                    file_size
                ))
                
                # Insert dependencies
                if 'dependencies' in manifest:
                    for dep_name, dep_version in manifest['dependencies'].items():
                        conn.execute("""
                            INSERT INTO plugin_dependencies 
                            (plugin_id, dependency_name, dependency_version)
                            VALUES (?, ?, ?)
                        """, (manifest['id'], dep_name, dep_version))
            
            return {"success": True, "plugin_id": manifest['id']}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get plugin information by ID"""
        with self.db.get_db() as conn:
            cursor = conn.execute("""
                SELECT * FROM plugin_registry WHERE id = ?
            """, (plugin_id,))
            row = cursor.fetchone()
            
            if row:
                plugin = dict(row)
                plugin['manifest'] = json.loads(plugin['manifest'])
                plugin['tags'] = json.loads(plugin['tags'] or '[]')
                
                # Get dependencies
                cursor = conn.execute("""
                    SELECT dependency_name, dependency_version, is_optional 
                    FROM plugin_dependencies WHERE plugin_id = ?
                """, (plugin_id,))
                plugin['dependencies'] = [dict(dep) for dep in cursor.fetchall()]
                
                return plugin
        return None
    
    def search_plugins(self, query: str = "", category: str = "", tags: List[str] = None, 
                      limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """Search plugins in the marketplace"""
        sql = """
            SELECT * FROM plugin_registry 
            WHERE status = 'approved'
        """
        params = []
        
        if query:
            sql += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if tags:
            for tag in tags:
                sql += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        sql += " ORDER BY is_featured DESC, rating DESC, downloads DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.db.get_db() as conn:
            cursor = conn.execute(sql, params)
            plugins = []
            
            for row in cursor.fetchall():
                plugin = dict(row)
                plugin['manifest'] = json.loads(plugin['manifest'])
                plugin['tags'] = json.loads(plugin['tags'] or '[]')
                plugins.append(plugin)
        
        return {
            "plugins": plugins,
            "total": len(plugins),
            "limit": limit,
            "offset": offset
        }
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all plugin categories with counts"""
        with self.db.get_db() as conn:
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count 
                FROM plugin_registry 
                WHERE status = 'approved'
                GROUP BY category 
                ORDER BY count DESC
            """)
            return [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    def get_featured_plugins(self, limit: int = 6) -> List[Dict[str, Any]]:
        """Get featured plugins for homepage"""
        with self.db.get_db() as conn:
            cursor = conn.execute("""
                SELECT * FROM plugin_registry 
                WHERE status = 'approved' AND is_featured = TRUE
                ORDER BY rating DESC, downloads DESC
                LIMIT ?
            """, (limit,))
            
            plugins = []
            for row in cursor.fetchall():
                plugin = dict(row)
                plugin['manifest'] = json.loads(plugin['manifest'])
                plugin['tags'] = json.loads(plugin['tags'] or '[]')
                plugins.append(plugin)
            
            return plugins
    
    def update_plugin_stats(self, plugin_id: str, downloads: int = None, 
                           rating: float = None, rating_count: int = None):
        """Update plugin statistics"""
        updates = []
        params = []
        
        if downloads is not None:
            updates.append("downloads = downloads + ?")
            params.append(downloads)
        
        if rating is not None and rating_count is not None:
            updates.append("rating = ?, rating_count = ?")
            params.extend([rating, rating_count])
        
        if updates:
            sql = f"UPDATE plugin_registry SET {', '.join(updates)} WHERE id = ?"
            params.append(plugin_id)
            
            with self.db.get_db() as conn:
                conn.execute(sql, params)
    
    def approve_plugin(self, plugin_id: str, is_featured: bool = False) -> bool:
        """Approve a plugin for the marketplace"""
        try:
            with self.db.get_db() as conn:
                conn.execute("""
                    UPDATE plugin_registry 
                    SET status = 'approved', is_verified = TRUE, is_featured = ?
                    WHERE id = ?
                """, (is_featured, plugin_id))
            return True
        except Exception:
            return False
    
    def reject_plugin(self, plugin_id: str, reason: str = "") -> bool:
        """Reject a plugin submission"""
        try:
            with self.db.get_db() as conn:
                conn.execute("""
                    UPDATE plugin_registry 
                    SET status = 'rejected'
                    WHERE id = ?
                """, (plugin_id,))
            return True
        except Exception:
            return False
    
    def get_user_plugins(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all plugins installed by a user"""
        with self.db.get_db() as conn:
            cursor = conn.execute("""
                SELECT pr.*, pi.installed_at, pi.is_active, pi.config
                FROM plugin_registry pr
                JOIN plugin_installations pi ON pr.id = pi.plugin_id
                WHERE pi.user_id = ?
                ORDER BY pi.installed_at DESC
            """, (user_id,))
            
            plugins = []
            for row in cursor.fetchall():
                plugin = dict(row)
                plugin['manifest'] = json.loads(plugin['manifest'])
                plugin['tags'] = json.loads(plugin['tags'] or '[]')
                if plugin['config']:
                    plugin['config'] = json.loads(plugin['config'])
                plugins.append(plugin)
            
            return plugins
    
    def clear_cache(self):
        """Clear the registry cache"""
        self.registry_cache.clear()