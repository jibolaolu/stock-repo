# Use the official Nginx image to serve the frontend

FROM nginx:alpine

# Copy the frontend static files to the nginx public directory
COPY index.html /usr/share/nginx/html
COPY header.png /usr/share/nginx/html
COPY default.conf /etc/nginx/conf.d/default.conf

# Expose the default HTTP port
EXPOSE 80

