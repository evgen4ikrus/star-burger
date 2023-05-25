FROM node:16
RUN npm install -g npm@9.6.7

WORKDIR /code/
COPY package.json package-lock.json /code/
RUN npm ci --include=dev
COPY . /code/

EXPOSE 8080
