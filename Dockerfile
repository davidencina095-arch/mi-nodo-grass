FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl nodejs npm
RUN npm install -g grass-node || npm install -g @grass/cli || true
EXPOSE 8080
CMD python3 -m http.server 8080 & npx grass-cli --user \ --pass \ || tail -f /dev/null
