#!/usr/bin/env python3
"""
Setup script for YouTube Automation Platform
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {command}: {str(e)}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = {
        'docker': 'Docker',
        'docker-compose': 'Docker Compose',
        'git': 'Git',
        'python3': 'Python 3',
        'pip3': 'pip3'
    }
    
    missing = []
    for cmd, name in dependencies.items():
        if not shutil.which(cmd):
            missing.append(name)
    
    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nPlease install missing dependencies and run setup again.")
        return False
    
    return True

def setup_environment():
    """Setup environment file"""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("Created .env file from .env.example")
        print("Please edit .env file with your API keys and configuration")
    else:
        print(".env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = [
        'assets/images',
        'assets/clips', 
        'assets/audio',
        'configs',
        'plugins',
        'models',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def setup_models_directory():
    """Setup models directory with initial structure"""
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    # Create subdirectories for different model types
    model_subdirs = [
        'sdxl',
        'controlnet',
        'lora',
        'animatediff',
        'zeroscope',
        'tts',
        'torch_cache'
    ]
    
    for subdir in model_subdirs:
        (models_dir / subdir).mkdir(exist_ok=True)
        print(f"Created model directory: models/{subdir}")

def download_initial_models():
    """Download initial AI models (optional)"""
    print("\nModel Download Options:")
    print("1. Download all models now (requires ~20GB storage)")
    print("2. Download models on first use (recommended)")
    print("3. Skip model download")
    
    choice = input("Choose option (1-3) [2]: ").strip() or "2"
    
    if choice == "1":
        print("Downloading models... This will take a while.")
        # Would implement model downloading here
        print("Model downloading not implemented in setup script.")
        print("Models will be downloaded automatically on first use.")
    elif choice == "2":
        print("Models will be downloaded on first use.")
    else:
        print("Skipping model download.")

def build_docker_images():
    """Build Docker images"""
    print("Building Docker images...")
    
    if not run_command("docker-compose build"):
        print("Failed to build Docker images")
        return False
    
    print("Docker images built successfully")
    return True

def setup_database():
    """Initialize database"""
    print("Initializing database...")
    
    # Create database file
    db_file = Path('youtube_automation.db')
    if not db_file.exists():
        db_file.touch()
        print("Created database file")
    
    return True

def main():
    """Main setup function"""
    print("YouTube Automation Platform Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Create directories
    create_directories()
    setup_models_directory()
    
    # Setup database
    setup_database()
    
    # Ask about Docker setup
    build_docker = input("\nBuild Docker images now? (y/N): ").strip().lower()
    if build_docker in ('y', 'yes'):
        if not build_docker_images():
            print("Docker build failed, but you can run 'docker-compose build' later")
    
    # Ask about model download
    download_initial_models()
    
    print("\n" + "=" * 40)
    print("Setup Complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: docker-compose up -d")
    print("3. Access the dashboard at http://localhost:3000")
    print("4. Access the API docs at http://localhost:8000/api/docs")
    print("5. Monitor tasks at http://localhost:5555 (Flower)")
    
    print("\nFor development:")
    print("- Backend: cd backend && python main.py")
    print("- Frontend: cd frontend && bun dev")
    
    print("\nDocumentation: See README.md for detailed instructions")

if __name__ == "__main__":
    main()