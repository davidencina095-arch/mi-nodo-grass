FROM node:18-alpine
RUN npm install -g @eliasyoy/grass-cli || true
CMD tail -f /dev/null
