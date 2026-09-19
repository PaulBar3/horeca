"""
Gunicorn configuration for FOODCORE.
"""

import os

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = int(os.environ.get("GUNICORN_WORKERS", 3))
worker_class = "sync"
worker_tmp_dir = "/dev/shm"

# Timeout
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "foodcore"

# Server mechanics
preload_app = True
tmp_upload_dir = None
