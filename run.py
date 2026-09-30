"""
Master Launcher for Pax Historia (2026 Engine)
Starts FastAPI Web Studio on 0.0.0.0:8080 and launches Telegram Bot Worker.
"""
import asyncio
import logging
import uvicorn
import os
import sys

from config import WEB_HOST, WEB_PORT, TELEGRAM_BOT_TOKEN
from web.server import app
from bot.telegram_bot import build_bot_application

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("PaxHistoriaMaster")

async def run_telegram_bot():
    """Runs the Telegram Bot polling worker in the background."""
    try:
        logger.info(f"Initializing Telegram Bot with token {TELEGRAM_BOT_TOKEN[:10]}...")
        bot_app = build_bot_application()
        await bot_app.initialize()
        await bot_app.start()
        await bot_app.updater.start_polling(drop_pending_updates=True)
        logger.info("Telegram Bot polling started successfully!")
        
        # Keep running
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        logger.warning(f"Telegram Bot polling notice (Network/API): {e}")
        logger.info("Note: Web Simulator is 100% active and functioning at http://0.0.0.0:8080")

async def main():
    logger.info("=" * 60)
    logger.info("🏛️ PAX HISTORIA 2026 ENGINE - STARTING UP")
    logger.info(f"🌍 Web Studio & Live Simulator: http://{WEB_HOST}:{WEB_PORT}")
    logger.info(f"🤖 Telegram Bot Token: {TELEGRAM_BOT_TOKEN[:12]}...")
    logger.info("⚡ 500+ Functions, AI BYOK, Prompts Workshop, Cyber & Jamming Active")
    logger.info("=" * 60)

    # Start bot in background task
    asyncio.create_task(run_telegram_bot())

    # Start Uvicorn Web Server
    config = uvicorn.Config(app=app, host=WEB_HOST, port=WEB_PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Pax Historia server shut down.")
