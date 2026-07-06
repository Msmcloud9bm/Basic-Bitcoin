# Dockerfile

# Build a minimal Node app image that runs server/index.js and serves client/dist
FROM node:18-alpine AS build
WORKDIR /app

# Copy server files and install production deps
COPY server/package.json server/package-lock.json* ./server/
RUN cd server && npm ci --production

# Copy server source
COPY server/ ./server/

# Copy built client dist if present (CI should build client beforehand)
COPY client/dist ./client/dist

WORKDIR /app/server
EXPOSE 4000

# Entrypoint
CMD ["node", "index.js"]
