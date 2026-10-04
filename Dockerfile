# SIH26146 — Containerized Offline Forensic Intelligence Workstation
# Team COGNOVAX (Team ID: 162623) | Sponsoring Agency: NTRO
# Core Target: Linux Offline Execution

FROM python:3.11-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install curl for internal health-checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source repository
COPY . .

# Ensure shell scripts have execution permissions
RUN chmod +x *.sh 2>/dev/null || true

# Expose local dashboard port
EXPOSE 8000

# Healthcheck to verify local air-gapped readiness
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/api/health || exit 1

# Default command launches offline dashboard service
CMD ["python", "main.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
