# 阶段 1:构建 Vue SPA(node:20)
FROM node:20-alpine AS builder
WORKDIR /app

# 先拷 package 文件,利用 docker 层缓存(.dockerignore 已排除 node_modules)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# 拷源码并构建 → /app/dist
COPY frontend/ .
RUN npm run build

# 阶段 2:nginx 托管 dist(与后端 web 服务同 compose 网络)
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
