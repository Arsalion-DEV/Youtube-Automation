module.exports = {
  apps: [
    {
      name: "youtube-automation-backend-prod",
      script: "./venv/bin/python",
      args: "production_main.py --host 0.0.0.0 --port 8001",
      cwd: "/home/ubuntu/Youtube-Automation/backend",
      env: {
        PYTHONPATH: "/home/ubuntu/Youtube-Automation/backend",
        NODE_ENV: "production",
        ENVIRONMENT: "production"
      },
      instances: 1,
      exec_mode: "fork",
      watch: false,
      max_memory_restart: "400M",
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: "10s",
      log_file: "/var/log/youtube-automation-backend.log",
      error_file: "/var/log/youtube-automation-backend-error.log",
      out_file: "/var/log/youtube-automation-backend-out.log"
    },
    {
      name: "youtube-automation-frontend-prod",
      script: "npm",
      args: "run build && npm run start",
      cwd: "/home/ubuntu/Youtube-Automation/frontend",
      instances: 1,
      exec_mode: "fork",
      watch: false,
      max_memory_restart: "500M",
      restart_delay: 3000,
      env: {
        NODE_ENV: "production",
        PORT: 3000,
        NEXT_PUBLIC_API_URL: "http://13.60.77.139:8001",
        NEXT_TELEMETRY_DISABLED: 1
      },
      log_file: "/var/log/youtube-automation-frontend.log",
      error_file: "/var/log/youtube-automation-frontend-error.log",
      out_file: "/var/log/youtube-automation-frontend-out.log"
    },
    {
      name: "youtube-automation-celery-worker",
      script: "./venv/bin/python",
      args: "-m celery -A production_main.celery worker --loglevel=info --concurrency=2",
      cwd: "/home/ubuntu/Youtube-Automation/backend",
      env: {
        PYTHONPATH: "/home/ubuntu/Youtube-Automation/backend",
        ENVIRONMENT: "production"
      },
      instances: 1,
      exec_mode: "fork",
      watch: false,
      max_memory_restart: "800M",
      restart_delay: 10000,
      max_restarts: 5,
      min_uptime: "30s",
      log_file: "/var/log/youtube-automation-celery.log"
    }
  ]
};