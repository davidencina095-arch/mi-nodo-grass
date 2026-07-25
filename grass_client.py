#!/usr/bin/env python3
import asyncio
import json
import os
import ssl
import uuid
import logging
import requests
import websockets

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

USER = os.environ.get("GRASS_USERNAME", "")
PASS = os.environ.get("GRASS_PASSWORD", "")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def get_token(email, password):
    url = "https://api.getgrass.io/login"
    resp = requests.post(url, json={"username": email, "password": password}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("result", {}).get("accessToken") or data.get("accessToken")
    log.info(f"Login OK, token: {token[:20]}...")
    return token

def get_user_id(token):
    url = "https://api.getgrass.io/users/me"
    resp = requests.get(url, headers={"Authorization": token}, timeout=30)
    resp.raise_for_status()
    uid = resp.json().get("result", {}).get("userId") or resp.json().get("userId")
    log.info(f"User ID: {uid}")
    return uid

async def connect(token, user_id):
    device_id = str(uuid.uuid4())
    ws_url = "wss://proxy2.wynd.network:4444/"
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    headers = {
        "User-Agent": USER_AGENT,
        "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi",
    }
    log.info(f"Connecting to Grass WS as device {device_id}...")
    async with websockets.connect(ws_url, ssl=ssl_ctx, extra_headers=headers, ping_interval=20, ping_timeout=20) as ws:
        # Send AUTH
        auth_msg = {
            "id": str(uuid.uuid4()),
            "version": "1.0.0",
            "action": "AUTH",
            "data": {
                "browser_id": device_id,
                "user_id": user_id,
                "user_agent": USER_AGENT,
                "timestamp": 0,
                "device_type": "extension",
                "version": "4.28.1",
            }
        }
        await ws.send(json.dumps(auth_msg))
        log.info("AUTH sent, waiting for response...")
        async for raw in ws:
            msg = json.loads(raw)
            action = msg.get("action", "")
            log.info(f"<< {action}")
            if action == "AUTH":
                log.info("Authenticated successfully!")
                pong = {"id": msg["id"], "origin_action": "AUTH"}
                await ws.send(json.dumps(pong))
            elif action == "PONG":
                pong = {"id": msg["id"], "origin_action": "PONG"}
                await ws.send(json.dumps(pong))
            elif action == "HTTP_REQUEST":
                payload = msg.get("data", {})
                result = {"url": payload.get("url", ""), "status": 200, "status_text": "OK", "headers": {}, "body": ""}
                resp = {"id": msg["id"], "origin_action": "HTTP_REQUEST", "result": result}
                await ws.send(json.dumps(resp))

async def main():
    if not USER or not PASS:
        log.error("GRASS_USERNAME and GRASS_PASSWORD env vars are required")
        return
    while True:
        try:
            token = get_token(USER, PASS)
            user_id = get_user_id(token)
            await connect(token, user_id)
        except Exception as e:
            log.error(f"Error: {e}, reconnecting in 10s...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
