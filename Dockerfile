FROM python:3.11-slim
RUN pip install --no-cache-dir requests websockets
WORKDIR /app
COPY grass_client.py .
EXPOSE 8080
CMD python3 -m http.server 8080 & python3 /app/grass_client.py
