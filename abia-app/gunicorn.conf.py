# Gunicorn configuration for Abia Migration Observatory
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "-"
accesslog = "-"
capture_output = True
enable_stdio_inheritance = True
