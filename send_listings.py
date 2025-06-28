import os
import requests
import urllib.parse
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
APIFY_DATASET_URL = os.getenv("APIFY_DATASET_URL")


async def send_rental_summary(bot_token, chat_id, listings):
    bot = Bot(token=bot_token)

    if not listings:
        message = "❌ No new listings found today."
    else:
        message = "🏡 <b>New Rental Listings</b>\n\n"
        for i, listing in enumerate(listings, 1):
            clean_url = urllib.parse.quote(listing['url'], safe=':/?=&')
            message += (
                f"{i}. <b>{listing['location']}</b>\n"
                f"{listing['rooms']} Rooms • {listing['size']} m² • {listing['floor']}\n"
                f"₪{listing['price']}/month\n"
                f"{listing['features']}\n"
                f"<a href=\"{clean_url}\">View Listing</a>\n\n"
            )

    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


async def main():
    response = requests.get(APIFY_DATASET_URL)
    items = response.json()
    listings = []

    for item in items:
        try:
            listings.append({
                "location": item.get("location", "Unknown location"),
                "rooms": item.get("rooms", "N/A"),
                "size": item.get("sqm", "N/A"),
                "floor": item.get("floor", "N/A"),
                "price": item.get("price", "N/A"),
                "balcony": item.get("balcony", "N/A"),
                "features": item.get("description", "")[:60] + "...",
                "url": item.get("item_url", "#")
            })
        except Exception:
            continue

    await send_rental_summary(BOT_TOKEN, CHAT_ID, listings[:5])


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
