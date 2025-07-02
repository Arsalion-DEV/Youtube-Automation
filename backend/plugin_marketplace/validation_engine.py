"""
Plugin Validation Engine
Security validation and sandboxing for plugins
"""

import ast
import os
import json
import zipfile
import tempfile
import subprocess
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import hashlib
import magic
from datetime import datetime

class PluginValidationEngine:
    def __init__(self):
        self.dangerous_imports = {
            'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib', 'requests',
            'importlib', '__import__', 'eval', 'exec', 'compile', 'open',
            'file', 'input', 'raw_input'
        }
        
        self.dangerous_functions = {
            'eval', 'exec', 'compile', '__import__', 'getattr', 'setattr',
            'delattr', 'hasattr', 'globals', 'locals', 'vars', 'dir'
        }
        
        self.allowed_file_types = {
            '.py', '.json', '.yaml', '.yml', '.txt', '.md', '.html', '.css', 
            '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg'
        }
        
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.max_files = 100
    
    def validate_plugin(self, plugin_file: str) -> Dict[str, Any]:
        """Complete plugin validation"""
        results = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "security_score": 0,
            "file_info": {},
            "manifest": None
        }
        
        try:
            # Basic file checks
            file_check = self._validate_file_basic(plugin_file)
            if not file_check["valid"]:
                results["errors"].extend(file_check["errors"])
                return results
            
            results["file_info"] = file_check["info"]
            
            # Extract and validate archive
            with tempfile.TemporaryDirectory() as temp_dir:
                extract_result = self._extract_plugin(plugin_file, temp_dir)
                if not extract_result["valid"]:
                    results["errors"].extend(extract_result["errors"])
                    return results
                
                # Validate manifest
                manifest_result = self._validate_manifest(temp_dir)
                if not manifest_result["valid"]:
                    results["errors"].extend(manifest_result["errors"])
                    return results
                
                results["manifest"] = manifest_result["manifest"]
                
                # Security validation
                security_result = self._validate_security(temp_dir)
                results["security_score"] = security_result["score"]
                results["warnings"].extend(security_result["warnings"])
                results["errors"].extend(security_result["errors"])
                
                # Code quality checks
                quality_result = self._validate_code_quality(temp_dir)
                results["warnings"].extend(quality_result["warnings"])
                
                # Dependencies validation
                deps_result = self._validate_dependencies(results["manifest"])
                results["warnings"].extend(deps_result["warnings"])
                results["errors"].extend(deps_result["errors"])
            
            # Final validation
            results["valid"] = len(results["errors"]) == 0 and results["security_score"] >= 70
            
        except Exception as e:
            results["errors"].append(f"Validation failed: {str(e)}")
        
        return results
    
    def _validate_file_basic(self, plugin_file: str) -> Dict[str, Any]:
        """Basic file validation"""
        result = {"valid": False, "errors": [], "info": {}}
        
        if not os.path.exists(plugin_file):
            result["errors"].append("Plugin file not found")
            return result
        
        # File size check
        file_size = os.path.getsize(plugin_file)
        if file_size > self.max_file_size:
            result["errors"].append(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            return result
        
        # File type check
        try:
            file_type = magic.from_file(plugin_file, mime=True)
            if file_type not in ['application/zip', 'application/x-zip-compressed']:
                result["errors"].append(f"Invalid file type: {file_type} (expected ZIP)")
                return result
        except:
            result["warnings"] = ["Could not determine file type"]
        
        # Calculate hash
        with open(plugin_file, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        result["info"] = {
            "size": file_size,
            "hash": file_hash,
            "type": file_type if 'file_type' in locals() else 'unknown'
        }
        result["valid"] = True
        return result
    
    def _extract_plugin(self, plugin_file: str, extract_dir: str) -> Dict[str, Any]:
        """Extract and validate plugin archive"""
        result = {"valid": False, "errors": []}
        
        try:
            with zipfile.ZipFile(plugin_file, 'r') as zip_ref:
                # Check number of files
                if len(zip_ref.namelist()) > self.max_files:
                    result["errors"].append(f"Too many files: {len(zip_ref.namelist())} (max: {self.max_files})")
                    return result
                
                # Validate file paths
                for file_path in zip_ref.namelist():
                    # Check for directory traversal
                    if '..' in file_path or file_path.startswith('/'):
                        result["errors"].append(f"Dangerous file path: {file_path}")
                        return result
                    
                    # Check file extension
                    if not any(file_path.endswith(ext) for ext in self.allowed_file_types):
                        if not file_path.endswith('/'):  # Allow directories
                            result["errors"].append(f"Disallowed file type: {file_path}")
                            return result
                
                # Extract files
                zip_ref.extractall(extract_dir)
                result["valid"] = True
                
        except zipfile.BadZipFile:
            result["errors"].append("Invalid ZIP file")
        except Exception as e:
            result["errors"].append(f"Extraction failed: {str(e)}")
        
        return result
    
    def _validate_manifest(self, plugin_dir: str) -> Dict[str, Any]:
        """Validate plugin manifest"""
        result = {"valid": False, "errors": [], "manifest": None}
        
        manifest_path = os.path.join(plugin_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            result["errors"].append("Missing manifest.json")
            return result
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Required fields
            required_fields = [
                'id', 'name', 'version', 'author', 'description',
                'category', 'entry_point', 'api_version'
            ]
            
            for field in required_fields:
                if field not in manifest:
                    result["errors"].append(f"Missing required field: {field}")
            
            # Validate field formats
            if 'id' in manifest:
                if not re.match(r'^[a-z0-9_-]+$', manifest['id']):
                    result["errors"].append("Invalid plugin ID format")
            
            if 'version' in manifest:
                if not re.match(r'^\d+\.\d+\.\d+$', manifest['version']):
                    result["errors"].append("Invalid version format (use semver)")
            
            if 'category' in manifest:
                valid_categories = [
                    'ai-models', 'content-tools', 'analytics', 
                    'automation', 'integrations', 'utilities'
                ]
                if manifest['category'] not in valid_categories:
                    result["errors"].append(f"Invalid category: {manifest['category']}")
            
            # Validate entry point exists
            if 'entry_point' in manifest:
                entry_path = os.path.join(plugin_dir, manifest['entry_point'])
                if not os.path.exists(entry_path):
                    result["errors"].append(f"Entry point not found: {manifest['entry_point']}")
            
            result["manifest"] = manifest
            result["valid"] = len(result["errors"]) == 0
            
        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON in manifest: {str(e)}")
        except Exception as e:
            result["errors"].append(f"Manifest validation failed: {str(e)}")
        
        return result
    
    def _validate_security(self, plugin_dir: str) -> Dict[str, Any]:
        """Security validation of plugin code"""
        result = {"score": 100, "errors": [], "warnings": []}
        
        try:
            for root, dirs, files in os.walk(plugin_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        file_result = self._validate_python_file(file_path)
                        
                        result["score"] -= file_result["penalty"]
                        result["warnings"].extend(file_result["warnings"])
                        result["errors"].extend(file_result["errors"])
            
            # Minimum security score
            if result["score"] < 0:
                result["score"] = 0
                
        except Exception as e:
            result["errors"].append(f"Security validation failed: {str(e)}")
            result["score"] = 0
        
        return result
    
    def _validate_python_file(self, file_path: str) -> Dict[str, Any]:
        """Validate individual Python file for security"""
        result = {"penalty": 0, "warnings": [], "errors": []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST for analysis
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                result["errors"].append(f"Syntax error in {file_path}: {str(e)}")
                result["penalty"] += 50
                return result
            
            # Check for dangerous imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.dangerous_imports:
                            result["warnings"].append(f"Dangerous import: {alias.name} in {file_path}")
                            result["penalty"] += 10
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.dangerous_imports:
                        result["warnings"].append(f"Dangerous import: {node.module} in {file_path}")
                        result["penalty"] += 10
                
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.dangerous_functions:
                            result["errors"].append(f"Dangerous function: {node.func.id} in {file_path}")
                            result["penalty"] += 30
            
            # Pattern-based checks
            dangerous_patterns = [
                r'__import__\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
                r'os\.system\s*\(',
                r'subprocess\.',
                r'socket\.',
                r'urllib\.',
                r'requests\.',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, content):
                    result["warnings"].append(f"Suspicious pattern found in {file_path}: {pattern}")
                    result["penalty"] += 5
                    
        except Exception as e:
            result["errors"].append(f"Failed to validate {file_path}: {str(e)}")
            result["penalty"] += 20
        
        return result
    
    def _validate_code_quality(self, plugin_dir: str) -> Dict[str, Any]:
        """Basic code quality checks"""
        result = {"warnings": []}
        
        try:
            python_files = []
            for root, dirs, files in os.walk(plugin_dir):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            if not python_files:
                result["warnings"].append("No Python files found")
                return result
            
            # Check for basic structure
            has_main = any('__main__' in open(f).read() for f in python_files)
            if not has_main:
                result["warnings"].append("No main entry point found")
            
            # Check for documentation
            has_docs = False
            for file_path in python_files:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if '"""' in content or "'''" in content:
                        has_docs = True
                        break
            
            if not has_docs:
                result["warnings"].append("No documentation found")
                
        except Exception as e:
            result["warnings"].append(f"Code quality check failed: {str(e)}")
        
        return result
    
    def _validate_dependencies(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Validate plugin dependencies"""
        result = {"warnings": [], "errors": []}
        
        if 'dependencies' not in manifest:
            return result
        
        dependencies = manifest['dependencies']
        if not isinstance(dependencies, dict):
            result["errors"].append("Dependencies must be a dictionary")
            return result
        
        # Check dependency versions
        for dep_name, dep_version in dependencies.items():
            if not isinstance(dep_name, str) or not isinstance(dep_version, str):
                result["errors"].append(f"Invalid dependency format: {dep_name}:{dep_version}")
                continue
            
            # Basic version format check
            if not re.match(r'^[\d\.\*\>\<\=\!\~\^]+$', dep_version):
                result["warnings"].append(f"Unusual version format: {dep_name}:{dep_version}")
        
        return result
    
    def get_validation_report(self, validation_result: Dict[str, Any]) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("=== PLUGIN VALIDATION REPORT ===\n")
        
        if validation_result["valid"]:
            report.append("✅ VALIDATION PASSED")
        else:
            report.append("❌ VALIDATION FAILED")
        
        report.append(f"Security Score: {validation_result['security_score']}/100\n")
        
        if validation_result["errors"]:
            report.append("ERRORS:")
            for error in validation_result["errors"]:
                report.append(f"  ❌ {error}")
            report.append("")
        
        if validation_result["warnings"]:
            report.append("WARNINGS:")
            for warning in validation_result["warnings"]:
                report.append(f"  ⚠️  {warning}")
            report.append("")
        
        if validation_result["manifest"]:
            manifest = validation_result["manifest"]
            report.append("PLUGIN INFO:")
            report.append(f"  Name: {manifest.get('name', 'Unknown')}")
            report.append(f"  Version: {manifest.get('version', 'Unknown')}")
            report.append(f"  Author: {manifest.get('author', 'Unknown')}")
            report.append(f"  Category: {manifest.get('category', 'Unknown')}")
        
        return "\n".join(report)