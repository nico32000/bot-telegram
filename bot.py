import os
import asyncio
import logging
import re
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import find_motorsport_deals

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]  # es. @fullrace_deals oppure -100xxxxxxxxxx
AFFILIATE_TAG = os.environ.get("AFFILIATE_TAG", "fullrace-21")
CHECK_INTERVAL_HOURS = int(os.environ.get("CHECK_INTERVAL_HOURS", "6"))

# Tiene traccia degli ASIN già postati (in memoria, si resetta al riavvio)
posted_asins = set()


def build_affiliate_url(asin: str) -> str:
    return f"https://www.amazon.it/dp/{asin}/?tag={AFFILIATE_TAG}"


def format_message(deal: dict) -> str:
    title = deal["title"]
    price = deal["price"]
    original_price = deal.get("original_price")
    discount_pct = deal.get("discount_pct")
    asin = deal["asin"]
    url = build_affiliate_url(asin)

    lines = []
    lines.append(f"🏁 <b>{title}</b>")
    lines.append("")

    if discount_pct and original_price:
        lines.append(f"💰 <s>{original_price}</s>  →  <b>{price}</b>  (-{discount_pct}%)")
    else:
        lines.append(f"💰 <b>{price}</b>")

    lines.append("")
    lines.append(f"🔗 <a href='{url}'>Vedi su Amazon</a>")
    lines.append("")
    lines.append("#motorsport #F1 #offerte #Amazon")

    return "\n".join(lines)


async def post_deals():
    bot = Bot(token=BOT_TOKEN)
    logger.info("Cerco offerte motorsport su Amazon...")

    deals = find_motorsport_deals()
    logger.info(f"Trovate {len(deals)} offerte totali")

    new_count = 0
    for deal in deals:
        asin = deal.get("asin")
        if not asin or asin in posted_asins:
            continue

        try:
            message = format_message(deal)
            image_url = deal.get("image_url")

            if image_url:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=image_url,
                    caption=message,
                    parse_mode=ParseMode.HTML
                )
            else:
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=False
                )

            posted_asins.add(asin)
            new_count += 1
            logger.info(f"Postato: {deal['title'][:50]}...")
            await asyncio.sleep(3)  # pausa tra un post e l'altro

        except Exception as e:
            logger.error(f"Errore nel postare {asin}: {e}")

    logger.info(f"Postati {new_count} nuovi prodotti")


async def main():
    logger.info("🏎️  MotorsportDealsBot avviato!")

    # Primo controllo subito all'avvio
    await post_deals()

    # Poi ogni X ore
    scheduler = AsyncIOScheduler()
    scheduler.add_job(post_deals, "interval", hours=CHECK_INTERVAL_HOURS)
    scheduler.start()

    logger.info(f"Scheduler attivo: controllo ogni {CHECK_INTERVAL_HOURS} ore")

    # Tieni il bot in vita
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
