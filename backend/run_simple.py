#!/usr/bin/env python3
"""
Simple server runner for YouTube Automation Platform
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

if __name__ == "__main__":
    import uvicorn
    
    # Run without httptools to avoid compatibility issues
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True,
        reload=False,  # Disable reload to avoid httptools issues
        http="h11",   # Use h11 instead of httptools
    )