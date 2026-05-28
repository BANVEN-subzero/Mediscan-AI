FROM nginx:alpine

# Copy nginx reverse proxy config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy all static frontend files to the default nginx location
COPY *.html *.js /usr/share/nginx/html/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1/ || exit 1

EXPOSE 80
