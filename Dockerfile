FROM node:18

# Install Python and Java
RUN apt-get update && apt-get install -y python3 python3-pip default-jre

WORKDIR /app

# Copy everything
COPY . .

# Install backend dependencies
RUN cd backend && npm install

# Install Python dependencies
RUN cd backend/python && pip3 install -r requirements.txt

# Install and build frontend
RUN cd frontend && npm install && npm run build

# Copy frontend build to backend
RUN cp -r frontend/build backend/build/

# Set working directory to backend
WORKDIR /app/backend

EXPOSE 5000
CMD ["node", "server.js"]