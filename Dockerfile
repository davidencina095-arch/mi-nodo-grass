FROM python:3.11-slim
RUN apt-get update && apt-get install -y wget procps curl
CMD wget https://github.com/grass-dev/grass-node/releases/latest/download/grass-node-linux-amd64 -O grass-node || true; chmod +x grass-node || true; tail -f /dev/null
