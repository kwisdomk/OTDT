# OT Digital Twin — React Dashboard
# Multi-stage: build with Node, serve with nginx

# Stage 1: Build
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci --legacy-peer-deps --silent

COPY . .

# Bake API URLs into the build (nginx proxies WS at runtime via docker network)
ARG REACT_APP_WS_URL=ws://localhost:8000/twin/stream
ARG REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_WS_URL=$REACT_APP_WS_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# Stage 2: Serve
FROM nginx:1.25-alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:3000 || exit 1

CMD ["nginx", "-g", "daemon off;"]
