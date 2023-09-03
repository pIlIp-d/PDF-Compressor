FROM node:latest

COPY frontend /frontend
RUN apt-get update

WORKDIR /frontend

RUN npm install
