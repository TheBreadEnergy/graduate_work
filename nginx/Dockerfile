FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf

COPY config /etc/nginx/conf.d/

COPY ssl /etc/nginx/ssl


EXPOSE 443

EXPOSE 80

EXPOSE 8080

