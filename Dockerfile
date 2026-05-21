FROM nginx:alpine

# Copy nginx reverse proxy config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the static HTML file as the main page
COPY mediscan-ai.html /usr/share/nginx/html/index.html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80
