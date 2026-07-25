FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl nodejs npm git
RUN git clone https://github.com/mrcolorr/get-grass.git /app || true
EXPOSE 8080
CMD python3 -m http.server 8080 & (cd /app && npm install && npm start) || tail -f /dev/null
