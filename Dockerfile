FROM node:18

# Install Python and Java for LanguageTool
RUN apt-get update && apt-get install -y python3 python3-pip default-jre

WORKDIR /app

# Copy backend files
COPY backend/package.json ./backend/
COPY backend/package-lock.json ./backend/ 2>/dev/null || true

# Install backend dependencies
RUN cd backend && npm install

# Copy backend source code
COPY backend/ ./backend/

# Install Python dependencies
RUN cd backend/python && pip3 install -r requirements.txt

# Copy frontend files
COPY frontend/package.json ./frontend/
COPY frontend/package-lock.json ./frontend/ 2>/dev/null || true

# Install and build frontend
RUN cd frontend && npm install && npm run build

# Create build directory in backend and copy frontend build
RUN mkdir -p backend/build && cp -r frontend/build/* backend/build/

# Set working directory to backend
WORKDIR /app/backend

EXPOSE 5000
CMD ["node", "server.js"]