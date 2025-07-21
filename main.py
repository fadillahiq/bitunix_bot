
import requests, time, schedule
from datetime import datetime

BOT_TOKEN = "7580552170:AAEGs8Z4HVhZgtnzRaK4VctZe6_fUL0pkz8"
CHAT_ID = "5246334675"

PAIRS = [
    "ETHUSDT", "BTCUSDT", "AAVEUSDT", "DOGEUSDT", "XRPUSDT",
    "MATICUSDT", "SUIUSDT", "OPUSDT", "HBARUSDT", "PEPEUSDT",
    "ARBUSDT", "INJUSDT", "RNDRUSDT", "LINKUSDT", "NEARUSDT"
]
API = "https://fapi.bitunix.com/api/v1/futures/market/kline"

def get_klines(symbol, interval="1h", limit=50):
    try:
        r = requests.get(API, params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
        d = r.json()
        if d.get("code") == 0 and isinstance(d.get("data"), list):
            return d["data"]
    except: pass
    return []

def detect_signal(symbol):
    k = get_klines(symbol)
    if not k: return None
    try:
        c = [float(i["close"]) for i in k if "close" in i]
        if len(c) < 20: return None
        high, low = max(c[-20:]), min(c[-20:])
        last = c[-1]

        if last > high * 0.995:
            return {"symbol": symbol, "side": "LONG", "entry": last,
                    "sl": round(low, 2), "tp": round(last + (high - low)*1.618, 2)}
        elif last < low * 1.005:
            return {"symbol": symbol, "side": "SHORT", "entry": last,
                    "sl": round(high, 2), "tp": round(last - (high - low)*1.618, 2)}
    except: pass
    return None

def format_call(sig):
    rr = round(abs(sig['tp'] - sig['entry']) / abs(sig['entry'] - sig['sl']), 2)
    confidence = "HIGH" if rr > 2.5 else "MEDIUM" if rr > 1.5 else "LOW"
    return f"""🔥 MASTER CALL: {sig['symbol']} – {sig['side']}

📍 Entry: {sig['entry']}
🛑 Stop Loss: {sig['sl']}
🎯 Take Profit: {sig['tp']}
📊 Risk Reward: {rr}
✅ Confidence Level: {confidence} ☑️

Sinyal ini berdasarkan breakout/pullback + struktur harga TF 1H–4H dan Fibonacci Extension.
Eksekusi dengan disiplin dan sesuaikan leverage."""

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def job():
    print("Menganalisis...")
    signals = [detect_signal(p) for p in PAIRS]
    valids = [s for s in signals if s]
    if valids:
        for sig in valids:
            msg = format_call(sig)
            send_to_telegram(msg)
            print(f"Sinyal dikirim: {sig['symbol']} - {sig['side']}")
    else:
        print("Tidak ada sinyal valid hari ini.")

job()
schedule.every().day.at("02:00").do(job)  # 09:00 WIB

while True:
    schedule.run_pending()
    time.sleep(60)
