FROM nginx:alpine

# Copy the static HTML file
COPY mediscan-ai.html /usr/share/nginx/html/

# Optional: Set it as index.html so it loads by default
COPY mediscan-ai.html /usr/share/nginx/html/index.html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80
