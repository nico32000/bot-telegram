import requests
import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Parole chiave motorsport per filtrare i prodotti
MOTORSPORT_KEYWORDS = [
    "formula 1", "formula1", "f1", "ferrari", "red bull racing", "mercedes amg",
    "mclaren", "alpine f1", "aston martin f1", "williams f1", "haas f1",
    "motogp", "moto gp", "valentino rossi", "marc marquez",
    "rally", "wrc", "dakar",
    "casco moto", "tuta racing", "guanti racing",
    "lego technic auto", "lego ferrari", "lego f1", "lego bugatti", "lego lamborghini",
    "modellino formula", "modellino f1", "die cast f1", "diecast racing",
    "sparco", "omp", "alpinestars", "sabelt",
    "pit stop", "racing", "motorsport",
    "pneumatici", "tires racing",
    "simulator f1", "sim racing", "volante racing", "thrustmaster", "fanatec", "logitech g29",
    "karting", "kart",
    "braccialetto hamilton", "cappellino ferrari", "maglietta racing",
]

# URL di ricerca Amazon Italia per categoria motorsport
SEARCH_URLS = [
    "https://www.amazon.it/s?k=formula+1+modellino&s=price-desc-rank",
    "https://www.amazon.it/s?k=lego+ferrari+f1&s=price-desc-rank",
    "https://www.amazon.it/s?k=sim+racing+volante&s=price-desc-rank",
    "https://www.amazon.it/s?k=casco+moto+racing&s=price-desc-rank",
    "https://www.amazon.it/s?k=ferrari+merchandise&s=price-desc-rank",
    "https://www.amazon.it/s?k=motogp+abbigliamento&s=price-desc-rank",
    "https://www.amazon.it/s?k=sparco+racing&s=price-desc-rank",
    "https://www.amazon.it/s?k=diecast+formula+1&s=price-desc-rank",
]

# Sconto minimo % per considerare un'offerta
MIN_DISCOUNT_PCT = 15


def is_motorsport(title: str) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in MOTORSPORT_KEYWORDS)


def extract_price(price_str: str) -> Optional[float]:
    """Converte stringa prezzo in float."""
    if not price_str:
        return None
    cleaned = re.sub(r"[^\d,\.]", "", price_str).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def scrape_search_page(url: str) -> List[Dict]:
    deals = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Status {response.status_code} per {url}")
            return deals

        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.select("div[data-asin][data-component-type='s-search-result']")

        for product in products:
            asin = product.get("data-asin", "").strip()
            if not asin:
                continue

            # Titolo
            title_el = product.select_one("h2 span")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)

            # Filtro motorsport
            if not is_motorsport(title):
                continue

            # Prezzo attuale
            price_el = product.select_one(".a-price .a-offscreen")
            price_str = price_el.get_text(strip=True) if price_el else None
            price_val = extract_price(price_str)

            # Prezzo originale (barrato)
            original_el = product.select_one(".a-price.a-text-price .a-offscreen")
            original_str = original_el.get_text(strip=True) if original_el else None
            original_val = extract_price(original_str)

            # Calcola sconto
            discount_pct = None
            if price_val and original_val and original_val > price_val:
                discount_pct = round((1 - price_val / original_val) * 100)

            # Mostra solo se c'è uno sconto sufficiente
            if discount_pct is None or discount_pct < MIN_DISCOUNT_PCT:
                continue

            # Badge sconto diretto Amazon (es. "-30%")
            badge_el = product.select_one(".s-coupon-unclipped, .a-badge-label")
            if badge_el and discount_pct is None:
                badge_text = badge_el.get_text(strip=True)
                match = re.search(r"(\d+)%", badge_text)
                if match:
                    discount_pct = int(match.group(1))

            # Immagine
            img_el = product.select_one("img.s-image")
            image_url = img_el.get("src") if img_el else None

            deals.append({
                "asin": asin,
                "title": title,
                "price": price_str,
                "original_price": original_str,
                "discount_pct": discount_pct,
                "image_url": image_url,
            })

            logger.info(f"✅ Trovata offerta: {title[:60]} (-{discount_pct}%)")

    except Exception as e:
        logger.error(f"Errore scraping {url}: {e}")

    return deals


def find_motorsport_deals() -> List[Dict]:
    all_deals = []
    seen_asins = set()

    for url in SEARCH_URLS:
        logger.info(f"Scraping: {url}")
        page_deals = scrape_search_page(url)
        for deal in page_deals:
            if deal["asin"] not in seen_asins:
                seen_asins.add(deal["asin"])
                all_deals.append(deal)

    # Ordina per sconto decrescente
    all_deals.sort(key=lambda x: x.get("discount_pct") or 0, reverse=True)
    logger.info(f"Totale offerte motorsport trovate: {len(all_deals)}")
    return all_deals


if __name__ == "__main__":
    # Test standalone
    logging.basicConfig(level=logging.INFO)
    deals = find_motorsport_deals()
    print(f"\nTrovate {len(deals)} offerte:")
    for d in deals[:5]:
        print(f"  - {d['title'][:60]} | {d['price']} (era {d['original_price']}) | -{d['discount_pct']}%")
