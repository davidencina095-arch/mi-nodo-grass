FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl
EXPOSE 8080
CMD python3 -m http.server 8080
