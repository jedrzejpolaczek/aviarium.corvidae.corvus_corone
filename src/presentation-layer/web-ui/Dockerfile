FROM nginx:alpine

COPY index.html /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]