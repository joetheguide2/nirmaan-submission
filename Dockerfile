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
    echo "=== Checking for package.json ===" && \
    find . -name "package.json" | head -10

# Install backend dependencies
RUN cd backend && npm install

# Install Python dependencies in virtual environment
RUN cd backend/python && python3 -m venv venv && \
    ./venv/bin/pip install -r requirements.txt

# Install and build frontend
RUN cd frontend && npm install && npm run build

# Copy frontend build to backend
RUN cp -r frontend/build backend/build/

# Set working directory to backend
WORKDIR /app/backend

EXPOSE 5000
CMD ["node", "server.js"]