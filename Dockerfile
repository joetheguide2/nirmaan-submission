FROM node:18

# Install Python, Java, and virtual environment tools
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv default-jre

WORKDIR /app

# Copy everything
COPY . .

# Debug: Show the structure to verify files are there
RUN echo "=== Checking project structure ===" && \
    ls -la && \
    echo "=== Frontend structure ===" && \
    ls -la frontend/ && \
    echo "=== Checking for public directory ===" && \
    find . -name "public" -type d && \
    echo "=== Checking for package.json ===" && \
    find . -name "package.json" | head -10

# Install backend dependencies
RUN cd backend && npm install

# Install Python dependencies in virtual environment
RUN cd backend/python && python3 -m venv venv && \
    ./venv/bin/pip install -r requirements.txt

# Check if frontend has the required structure
RUN echo "=== Frontend detailed structure ===" && \
    cd frontend && \
    ls -la && \
    echo "=== Public directory contents ===" && \
    ls -la public/ || echo "No public directory found"

# Install and build frontend (with error handling)
RUN cd frontend && npm install && \
    # Create public directory if it doesn't exist
    mkdir -p public && \
    # Check if we need to move index.html
    if [ ! -f public/index.html ] && [ -f ../index.html ]; then \
        echo "Moving index.html from root to frontend/public" && \
        cp ../index.html public/; \
    fi && \
    npm run build

# Copy frontend build to backend
RUN cp -r frontend/build backend/public/ || mkdir -p backend/public && cp -r frontend/build/* backend/public/

# Set working directory to backend
WORKDIR /app/backend

EXPOSE 5000
CMD ["node", "server.js"]