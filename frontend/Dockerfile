# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG NODE_VERSION=25.3.0

FROM node:${NODE_VERSION} AS builder

WORKDIR /app

ARG VITE_API_PROXY_TARGET
ENV VITE_API_PROXY_TARGET=${VITE_API_PROXY_TARGET}

# Copy dependency files first for caching
COPY package.json package-lock.json* ./

# Install deps (dev deps included)
RUN npm ci

COPY . .

# Vue dev server port
EXPOSE 5173

# For Vue CLI use: npm run serve
# For Vite use: npm run dev
CMD ["npm", "run", "dev", "--", "--host"]