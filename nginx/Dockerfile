FROM nginx:mainline-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.${APP_ENV}.conf /etc/nginx/conf.d
