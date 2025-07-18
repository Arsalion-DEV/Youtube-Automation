module.exports = {
  apps: [
    {
      name: "youtube-automation-backend",
      script: "./venv/bin/python",
      args: "production_optimized_main.py --host 0.0.0.0 --port 8001",
      cwd: "/home/ubuntu/Youtube-Automation/backend",
      env: {
        PYTHONPATH: "/home/ubuntu/Youtube-Automation/backend"
      },
      instances: 1,
      exec_mode: "fork",
      watch: false,
      max_memory_restart: "200M",
      restart_delay: 5000,
      max_restarts: 10,
      min_uptime: "10s"
    },
    {
      name: "youtube-automation-frontend",
      script: "npm",
      args: "run dev",
      cwd: "/home/ubuntu/Youtube-Automation/frontend",
      instances: 1,
      exec_mode: "fork",
      watch: false,
      max_memory_restart: "300M",
      restart_delay: 3000,
      env: {
        NODE_ENV: "development",
        PORT: 3000,
        NEXT_PUBLIC_API_URL: "http://13.60.77.139:8001"
      }
    }
  ]
};