FROM node:23-bookworm AS base

COPY . /app

WORKDIR /app

RUN npm install

FROM base AS development

CMD ["npm", "run", "dev"]

FROM base AS build

RUN npm run build

FROM nginx:alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config if you have one
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]