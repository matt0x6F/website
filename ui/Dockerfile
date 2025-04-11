FROM node:23-bookworm as base

COPY . /app

WORKDIR /app

RUN npm install

FROM base as development

CMD ["npm", "run", "dev"]

FROM base as build

RUN npm run build

FROM nginx:alpine as production

COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config if you have one
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]