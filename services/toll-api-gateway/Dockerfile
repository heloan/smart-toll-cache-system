# Toll API Gateway — NGINX Load Balancer
FROM nginx:latest

# Remove default NGINX config
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy main config and modular conf.d files
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

EXPOSE 80
