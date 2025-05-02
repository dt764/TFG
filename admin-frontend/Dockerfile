### STAGE 1: BUILD ###
FROM node:18.20.3-alpine3.19 AS build
WORKDIR /dist/src/app
COPY . .
RUN npm cache clean --force
RUN npm install
RUN npm run build --prod

### STAGE 2: RUN ###
FROM nginx:latest AS ngi
COPY --from=build /dist/src/app/dist/admin-frontend/browser /usr/share/nginx/html
COPY ./nginx.conf  /etc/nginx/conf.d/default.conf
EXPOSE 80
