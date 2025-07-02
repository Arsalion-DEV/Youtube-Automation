#!/usr/bin/env python3
"""
YouTube Automation Platform - System Monitor
Production monitoring script for health checks and performance metrics.
"""

import time
import json
import requests
import subprocess
from datetime import datetime

def check_backend_health():
    """Check backend API health"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        return response.status_code == 200, response.json()
    except:
        return False, {"error": "Backend unavailable"}

def check_frontend_health():
    """Check frontend availability"""
    try:
        response = requests.get("http://localhost:3001/", timeout=5)
        return response.status_code == 200, {"status": "Frontend operational"}
    except:
        return False, {"error": "Frontend unavailable"}

def check_redis_health():
    """Check Redis connection"""
    try:
        result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True, timeout=3)
        return result.stdout.strip() == "PONG", {"redis": "operational" if result.stdout.strip() == "PONG" else "failed"}
    except:
        return False, {"error": "Redis check failed"}

def get_resource_usage():
    """Get system resource usage"""
    try:
        # Get process info for uvicorn
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'uvicorn' in line and 'main:app' in line:
                parts = line.split()
                return {
                    "cpu_percent": parts[2],
                    "memory_percent": parts[3],
                    "memory_rss": parts[5]
                }
    except:
        pass
    return {"error": "Could not get resource usage"}

def monitor_system():
    """Run comprehensive system monitoring"""
    timestamp = datetime.now().isoformat()
    
    backend_ok, backend_data = check_backend_health()
    frontend_ok, frontend_data = check_frontend_health()
    redis_ok, redis_data = check_redis_health()
    resources = get_resource_usage()
    
    report = {
        "timestamp": timestamp,
        "overall_status": "healthy" if (backend_ok and frontend_ok and redis_ok) else "issues_detected",
        "services": {
            "backend": {"status": "healthy" if backend_ok else "error", "details": backend_data},
            "frontend": {"status": "healthy" if frontend_ok else "error", "details": frontend_data},
            "redis": {"status": "healthy" if redis_ok else "error", "details": redis_data}
        },
        "resources": resources
    }
    
    return report

if __name__ == "__main__":
    print("🔍 YouTube Automation Platform - System Monitor")
    print("=" * 50)
    
    report = monitor_system()
    print(f"📊 System Status: {report['overall_status'].upper()}")
    print(f"🕐 Timestamp: {report['timestamp']}")
    print()
    
    for service, data in report['services'].items():
        status_icon = "✅" if data['status'] == 'healthy' else "❌"
        print(f"{status_icon} {service.title()}: {data['status']}")
    
    print()
    if 'cpu_percent' in report['resources']:
        print(f"💾 Resource Usage:")
        print(f"   CPU: {report['resources']['cpu_percent']}%")
        print(f"   Memory: {report['resources']['memory_percent']}%")
        print(f"   RSS: {report['resources']['memory_rss']}KB")
    
    # Return exit code based on system health
    exit(0 if report['overall_status'] == 'healthy' else 1)