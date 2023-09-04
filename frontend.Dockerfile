FROM node:latest

COPY frontend/package-lock.json frontend/package.json frontend/tsconfig.json frontend/tsconfig.node.json frontend/vite.config.ts frontend/index.html /frontend/
COPY frontend/src /frontend/src

RUN apt-get update

WORKDIR /frontend

RUN npm install
