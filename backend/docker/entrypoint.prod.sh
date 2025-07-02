#!/bin/bash
set -e

echo "🚀 Starting YouTube Automation Platform in Production Mode"

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! pg_isready -h postgres -p 5432 -U $POSTGRES_USER; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "✅ Database is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
while ! redis-cli -h redis ping > /dev/null 2>&1; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
python -c "
import asyncio
from database import Database

async def init():
    db = Database()
    await db.initialize()
    print('Database initialized successfully')

asyncio.run(init())
"

# Warm up AI models if in GPU mode
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "🔥 Warming up AI models..."
    python -c "
try:
    from modules.script_gen.generator import ScriptGenerator
    from modules.t2i_sdxl_controlnet.generator import ImageGenerator
    print('AI models warmed up successfully')
except Exception as e:
    print(f'AI model warmup failed: {e}')
    print('Continuing without AI model warmup...')
"
fi

# Start the application
echo "🎬 Starting application..."
exec "$@"