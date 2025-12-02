# gunicorn_config.py
# Gunicorn configuration file

# The number of worker processes for handling requests.
# A common pattern is `2-4 x $(NUM_CORES)`.
workers = 2

# The socket to bind to. This can be an IP address and port,
# or a Unix socket path.
bind = "0.0.0.0:8000"

# The number of seconds to wait for a worker to respond to requests.
# A worker that doesn't respond in time will be restarted.
timeout = 30

# The type of workers to use. "sync" is the default and is fine for most cases.
# For high-concurrency, consider "eventlet", "gevent", or "meinheld".
worker_class = "sync"

# Log level
loglevel = "info"

# Path to the access log file. "-" means stdout.
accesslog = "-"

# Path to the error log file. "-" means stderr.
errorlog = "-"

# Name of the application module to run
# This should point to your Django project's WSGI file.
# e.g., "myproject.wsgi:application"
wsgi_app = "genquiz_web.wsgi:application"
