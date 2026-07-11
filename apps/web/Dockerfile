FROM node:24-alpine

RUN apk add --no-cache python3

WORKDIR /app
COPY . .

ENV HOST=0.0.0.0 \
    PORT=4173 \
    P0_DB_PATH=/data/p0.sqlite \
    PYTHON=python3

EXPOSE 4173

CMD ["node", "server.mjs"]
