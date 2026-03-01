FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json next.config.js next-env.d.ts /app/
COPY app /app/app
COPY lib /app/lib
RUN npm install
RUN npm run build
CMD ["npm", "run", "start"]
