# ─────────────────────────────────────────────
# Stage 1 — Builder
# Purpose: install all Python packages
# This stage has build tools we don't want
# in our final image
# ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Why set these env vars?
# PYTHONDONTWRITEBYTECODE stops Python writing .pyc files
# — we don't need them in a container
# PYTHONUNBUFFERED forces Python to print logs immediately
# — without this, logs get buffered and you can't see
# them in real time in Kubernetes
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Copy requirements first — before any code.
# Why? Docker caches each layer. If we copy code first,
# any code change invalidates the package cache and
# pip install runs again even if requirements didn't change.
# Copying requirements first means pip only reruns when
# requirements.txt actually changes.
COPY requirements.txt .

# Install packages into a specific folder /install
# so we can copy just that folder into stage 2
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─────────────────────────────────────────────
# Stage 2 — Final image
# Purpose: run the application
# Clean, minimal — no build tools
# ─────────────────────────────────────────────
FROM python:3.12-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user to run the app
# Why? If someone exploits your app and gets into
# the container, they should be an unprivileged user
# — not root. Root inside a container can mean
# root on the host in some configurations.
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --create-home appuser

WORKDIR /service

# Copy installed packages from builder stage
# We get all the packages without any build tools
COPY --from=builder /install /usr/local

# Copy the Django application code
COPY app/ .

# Change ownership of all files to appuser
# The app should own its own files
RUN chown -R appuser:appgroup /service

# Switch to non-root user
# Every command after this runs as appuser, not root
USER appuser

# Expose port 8000 — this is documentation more than
# enforcement. It tells anyone reading the Dockerfile
# that this container listens on 8000.
EXPOSE 8000

# Health check — Kubernetes uses this to know if the
# pod is ready to serve traffic. If this fails,
# Kubernetes won't send requests to this pod.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" \
    || exit 1

# Start command — Gunicorn instead of runserver
# --bind 0.0.0.0:8000   listen on all interfaces
# --workers 3           3 worker processes
# --timeout 120         kill workers taking over 2 min
# --access-logfile -    log to stdout (Kubernetes captures this)
# config.wsgi:application  the Django WSGI entry point
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--worker-tmp-dir", "/tmp", \
     "config.wsgi:application"]