#!/usr/bin/env python3
"""
Script to integrate the Channel Management System into the existing backend
"""

import sys
import os

def integrate_channel_manager():
    """Integrate channel management routes into simple_main.py"""
    
    # Read the current simple_main.py
    with open('simple_main.py', 'r') as f:
        content = f.read()
    
    # Check if already integrated
    if 'channel_api_routes' in content:
        print("Channel management already integrated")
        return
    
    # Find the imports section and add our import
    import_line = "from channel_api_routes import channel_bp, init_channel_manager"
    
    # Find where to add the import (after other imports)
    lines = content.split('\n')
    import_index = -1
    
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            import_index = i
    
    if import_index >= 0:
        lines.insert(import_index + 1, import_line)
    else:
        # Add at the beginning if no imports found
        lines.insert(0, import_line)
    
    # Find where to register the blueprint
    blueprint_line = "app.register_blueprint(channel_bp)"
    
    # Find the Flask app creation or blueprint registration section
    app_index = -1
    for i, line in enumerate(lines):
        if 'app =' in line and 'Flask' in line:
            app_index = i
            break
        elif 'register_blueprint' in line:
            app_index = i
            break
    
    if app_index >= 0:
        # Add after app creation or other blueprint registrations
        lines.insert(app_index + 1, blueprint_line)
        lines.insert(app_index + 2, "")  # Add blank line
    
    # Find where to add initialization
    init_line = "    init_channel_manager()  # Initialize channel management system"
    
    # Look for the main execution or startup section
    main_index = -1
    for i, line in enumerate(lines):
        if 'if __name__ ==' in line:
            main_index = i
            break
    
    if main_index >= 0:
        # Add initialization before app.run()
        for j in range(main_index, len(lines)):
            if 'app.run' in lines[j] or 'uvicorn.run' in lines[j]:
                lines.insert(j, init_line)
                break
    
    # Write the modified content back
    with open('simple_main.py', 'w') as f:
        f.write('\n'.join(lines))
    
    print("Successfully integrated channel management system")

if __name__ == "__main__":
    integrate_channel_manager()