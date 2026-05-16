import aiohttp

from core.utils.logger import logger


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async def send_alert(self, msg: str):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.api_url,
                    json={"chat_id": self.chat_id, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True},
                ) as response:
                    if response.status != 200:
                        logger.error(f"Telegram error: {await response.text()}")
            except Exception as e:
                logger.error(f"Failed to send Telegram: {e}")
