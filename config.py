import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

telegram_config = {
    "bot_token": os.getenv("TG_BOT_TOKEN", ""),
    "chat_id": os.getenv("TG_CHAT_ID", ""),
}

min_funding_rate = 0.5
left_show_time = 7
min_volume = 500_000
