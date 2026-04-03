FROM node:20-alpine

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

CMD ["npx", "vite", "preview", "--host", "0.0.0.0", "--port", "3000"]
