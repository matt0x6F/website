FROM node:21-bookworm as base

COPY . /app

WORKDIR /app

RUN npm install

FROM base as development

CMD ["npm", "run", "dev"]