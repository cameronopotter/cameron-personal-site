# Multi-stage production-optimized Dockerfile for Digital Greenhouse Frontend
# Optimized for minimal size, security, and performance

# ===================================
# Build Stage
# ===================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with frozen lockfile
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build arguments
ARG NODE_ENV=production
ARG VITE_API_BASE_URL
ARG VITE_WS_BASE_URL
ARG VITE_SENTRY_DSN
ARG VITE_GOOGLE_ANALYTICS_ID

# Set environment variables
ENV NODE_ENV=$NODE_ENV
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_BASE_URL=$VITE_WS_BASE_URL
ENV VITE_SENTRY_DSN=$VITE_SENTRY_DSN
ENV VITE_GOOGLE_ANALYTICS_ID=$VITE_GOOGLE_ANALYTICS_ID

# Build the application
RUN npm run build

# Optimize build output
RUN find dist -name "*.map" -delete && \
    find dist -name "*.ts" -delete && \
    find dist -name "*.tsx" -delete

# ===================================
# Production Stage
# ===================================
FROM nginx:1.25-alpine AS production

# Install security updates
RUN apk update && apk upgrade && apk add --no-cache \
    curl \
    tzdata \
    ca-certificates && \
    rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nginx -u 1001 -G nodejs

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy optimized nginx configuration
COPY docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY docker/nginx/security-headers.conf /etc/nginx/conf.d/security-headers.conf
COPY docker/nginx/gzip.conf /etc/nginx/conf.d/gzip.conf

# Copy built application from builder stage
COPY --from=builder --chown=nginx:nodejs /app/dist /usr/share/nginx/html

# Copy health check script
COPY docker/scripts/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Create necessary directories and set permissions
RUN mkdir -p /var/cache/nginx /var/log/nginx /var/run && \
    chown -R nginx:nodejs /var/cache/nginx /var/log/nginx /var/run /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Switch to non-root user
USER nginx

# Expose port 8080 (non-privileged)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Labels for metadata
LABEL maintainer="Cameron Potter <cameron@example.com>"
LABEL version="1.0.0"
LABEL description="Digital Greenhouse Frontend - Production Optimized"
LABEL org.opencontainers.image.source="https://github.com/cameronopotter/digital-greenhouse"

# Start nginx
CMD ["nginx", "-g", "daemon off;"]