# 🏎️ MotorsportDealsBot

Bot Telegram che trova automaticamente offerte Amazon su prodotti motorsport e le posta sul tuo canale con link affiliato.

---

## Come funziona

1. Ogni 6 ore (configurabile) scrapa Amazon.it cercando offerte motorsport
2. Filtra solo i prodotti con sconto ≥15%
3. Aggiunge automaticamente il tuo tag affiliato all'URL
4. Posta sul canale Telegram con immagine, titolo, prezzo barrato e sconto

---

## Setup su Railway

### 1. Prepara il bot Telegram
- Vai da [@BotFather](https://t.me/BotFather) su Telegram
- Crea un bot con `/newbot` e copia il token
- Aggiungi il bot come **admin** del tuo canale

### 2. Trova l'ID del tuo canale
- Se il canale è pubblico usa `@nome_canale`
- Se è privato, manda un messaggio al canale, poi apri:
  `https://api.telegram.org/bot<TOKEN>/getUpdates`
  e cerca `"chat":{"id":...}`

### 3. Deploy su Railway
1. Vai su [railway.app](https://railway.app) e fai login con GitHub
2. **New Project → Deploy from GitHub repo**
3. Carica questo progetto su GitHub (o usa "Deploy from local")
4. Vai su **Variables** e aggiungi:

| Variabile | Valore |
|-----------|--------|
| `BOT_TOKEN` | il token da BotFather |
| `CHANNEL_ID` | `@nome_canale` o `-100xxxxxxxxxx` |
| `AFFILIATE_TAG` | `fullrace-21` |
| `CHECK_INTERVAL_HOURS` | `6` (oppure `4`, `8`, ecc.) |

5. Railway fa il deploy automaticamente ✅

---

## Test locale

```bash
pip install -r requirements.txt

# Testa solo lo scraper
python scraper.py

# Avvia il bot (serve il .env)
cp .env.example .env
# modifica .env con i tuoi dati
python bot.py
```

---

## Struttura file

```
motorsport-deals-bot/
├── bot.py          # Logica principale + scheduler
├── scraper.py      # Scraping Amazon + filtro motorsport
├── requirements.txt
├── railway.toml    # Configurazione Railway
└── .env.example    # Variabili d'ambiente di esempio
```

---

## Personalizzazione

**Aggiungere parole chiave motorsport** → modifica `MOTORSPORT_KEYWORDS` in `scraper.py`

**Aggiungere categorie da cercare** → aggiungi URL in `SEARCH_URLS` in `scraper.py`

**Cambiare sconto minimo** → modifica `MIN_DISCOUNT_PCT` in `scraper.py` (default: 15%)

**Cambiare frequenza** → imposta `CHECK_INTERVAL_HOURS` nelle variabili Railway
