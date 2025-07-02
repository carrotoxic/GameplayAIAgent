# Use an official Python image for the final application
FROM python:3.11-slim

# Set the working directory
WORKDIR /app
# Install system dependencies: supervisor, node, npm, Java, and canvas dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    nodejs \
    npm \
    wget \
    ca-certificates \
    build-essential \
    libcairo2-dev \
    libpango1.0-dev \
    libjpeg-dev \
    libgif-dev \
    librsvg2-dev \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/java \
    && wget -O /tmp/openjdk.tar.gz https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.3%2B9/OpenJDK21U-jre_x64_linux_hotspot_21.0.3_9.tar.gz \
    && tar -xzf /tmp/openjdk.tar.gz -C /opt/java --strip-components=1 \
    && rm /tmp/openjdk.tar.gz \
    && update-alternatives --install /usr/bin/java java /opt/java/bin/java 1 \
    && update-alternatives --set java /opt/java/bin/java

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .
RUN echo "🧪 FULL DIRECTORY LISTING:" && find /app

# Clean any existing node_modules and install fresh
RUN rm -rf /app/infrastructure/adapters/game/minecraft/mineflayer_server/node_modules
RUN rm -rf /app/frontend/node_modules

# Install Node.js dependencies for the Mineflayer server
RUN npm install --prefix /app/infrastructure/adapters/game/minecraft/mineflayer_server

# Create eula.txt for Minecraft server
RUN echo "eula=true" > /app/infrastructure/adapters/game/minecraft/mineflayer_server/eula.txt

# Install Node.js dependencies and build the frontend
RUN npm install --prefix /app/frontend
RUN npm run build --prefix /app/frontend

# Expose ports for the services
EXPOSE 8000 3001 3002

# Start supervisor to manage all processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
 