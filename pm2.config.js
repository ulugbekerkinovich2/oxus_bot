module.exports = {
  apps: [
    {
      name: "oxus_bot",
      script: "app.py",
      interpreter: "./venv/bin/python",
      cwd: __dirname,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 3000,
      min_uptime: "10s",
      max_memory_restart: "500M",
      kill_timeout: 5000,
      env: {
        PYTHONUNBUFFERED: "1",
        PYTHONDONTWRITEBYTECODE: "1",
      },
      out_file: "./logs/bot.out.log",
      error_file: "./logs/bot.err.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      merge_logs: true,
    },
  ],
};
