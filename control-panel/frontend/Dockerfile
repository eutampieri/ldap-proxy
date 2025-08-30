FROM node:22 AS builder
COPY . /build
WORKDIR /build/control-panel/frontend
RUN npm ci
RUN npm run build

FROM nginx:alpine
COPY --from=builder /build/control-panel/frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
LABEL "traefik.http.routers.frontend.rule"="PathPrefix(`/`)"
