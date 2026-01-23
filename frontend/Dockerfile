# syntax=docker/dockerfile:1

ARG NODE_VERSION=25.3.0

FROM node:${NODE_VERSION} AS builder

WORKDIR /app

# Copy dependency files first for caching
COPY package.json package-lock.json* ./

# Install deps (dev deps included)
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]