FROM node:20-alpine
WORKDIR /app/frontend
COPY . ./
RUN npm install
RUN npm run build
EXPOSE 3000 
CMD ["npx", "-y", "serve", "dist"]