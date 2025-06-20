# Multi-stage build for Hub Service
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY package*.json pnpm-lock.yaml ./

# Install dependencies
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build frontend
RUN pnpm build

# Stage 2: Python backend with built frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Docker CLI
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
# Use host user's UID/GID for Docker socket access on macOS
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -r hubuser && useradd -r -u ${USER_ID} -g hubuser hubuser && \
    # Add user to the group that matches host Docker socket GID
    GROUP_NAME=$(getent group ${GROUP_ID} | cut -d: -f1) && \
    if [ -n "$GROUP_NAME" ]; then usermod -aG $GROUP_NAME hubuser; fi

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./dist

# Create necessary directories
RUN mkdir -p logs cache && \
    chown -R hubuser:hubuser /app

# Create entrypoint script to fix Docker socket permissions
COPY <<EOF /entrypoint.sh
#!/bin/bash
# Fix Docker socket permissions if it exists
if [ -S /var/run/docker.sock ]; then
    # Get the GID of the Docker socket
    DOCKER_GID=\$(stat -c '%g' /var/run/docker.sock)
    # Add hubuser to the group with that GID
    if ! groups hubuser | grep -q "\$DOCKER_GID"; then
        GROUP_NAME=\$(getent group \$DOCKER_GID | cut -d: -f1)
        if [ -n "\$GROUP_NAME" ]; then
            usermod -aG \$GROUP_NAME hubuser
        else
            groupadd -g \$DOCKER_GID docker_host
            usermod -aG docker_host hubuser
        fi
    fi
fi

# Switch to hubuser and run the application
exec gosu hubuser "\$@"
EOF

RUN chmod +x /entrypoint.sh && \
    # Install gosu for user switching
    apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:5003/api/health || exit 1

# Start the application with entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
