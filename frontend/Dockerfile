FROM node:18

WORKDIR /app

COPY package.json /app/

RUN npm install

COPY public/ /app/public
COPY src/ /app/src

EXPOSE 3000

CMD ["npm", "run", "start"]