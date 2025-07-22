
import requests, time, schedule
from datetime import datetime

BOT_TOKEN = "7580552170:AAEGs8Z4HVhZgtnzRaK4VctZe6_fUL0pkz8"
CHAT_ID = "5246334675"

PAIRS = [
    "ETHUSDT", "BTCUSDT", "AAVEUSDT", "DOGEUSDT", "XRPUSDT",
    "MATICUSDT", "SUIUSDT", "OPUSDT", "HBARUSDT", "PEPEUSDT",
    "ARBUSDT", "INJUSDT", "RNDRUSDT", "LINKUSDT", "NEARUSDT",
    "PENGUUSDT"
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
#ubah
def detect_smc_signal(symbol):
    k = get_klines(symbol, interval="1h", limit=50)
    if not k or len(k) < 30: return None
    try:
        closes = [float(i["close"]) for i in k if "close" in i]
        highs = [float(i["high"]) for i in k if "high" in i]
        lows = [float(i["low"]) for i in k if "low" in i]
        last = closes[-1]

        swing_high = max(highs[-30:-10])
        swing_low = min(lows[-30:-10])

        broke_up = any(h > swing_high for h in highs[-10:])
        broke_down = any(l < swing_low for l in lows[-10:])

        if broke_up and last > swing_high:
            fib_retracement = 0.618
            tp = round(swing_high - (swing_high - swing_low) * (1 - fib_retracement), 2)
            return {"symbol": symbol, "side": "LONG", "entry": last,
                    "sl": round(swing_low, 2), "tp": tp,
                    "smc": True}
        elif broke_down and last < swing_low:
            tp = round(swing_low + (swing_high - swing_low) * (1 - fib_retracement), 2)
            return {"symbol": symbol, "side": "SHORT", "entry": last,
                    "sl": round(swing_high, 2), "tp": tp,
                    "smc": True}
    except: pass
    return None

def detect_signal(symbol):
    fib_retracement = 0.618
    k = get_klines(symbol)
    if not k: return None
    try:
        c = [float(i["close"]) for i in k if "close" in i]
        if len(c) < 20: return None
        high, low = max(c[-20:]), min(c[-20:])
        last = c[-1]

        if last > high * 0.995:
            tp = round(high - (high - low) * (1 - fib_retracement), 2)
            return {"symbol": symbol, "side": "LONG", "entry": last,
                    "sl": round(low, 2), "tp": tp}
        elif last < low * 1.005:
            tp = round(low + (high - low) * (1 - fib_retracement), 2)
            return {"symbol": symbol, "side": "SHORT", "entry": last,
                    "sl": round(high, 2), "tp": tp}
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
Eksekusi dengan disiplin dan sesuaikan leverage.

"""
def send_to_discord(text):
    requests.post('https://discord.com/api/webhooks/1396241698929119273/9rzJbZXVoEgBWEZk69njsnFJe_whzG9av58lwBewII9owdqiP7-F0uDvM7f_DZzrh1Al', json={'content': text})
def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def job():
    print("Menganalisis...")
    signals = [detect_signal(p) for p in PAIRS]
    smc_signals = [detect_smc_signal(p) for p in PAIRS] #ubah
    signals += [s for s in smc_signals if s] #ubah
    valids = [s for s in signals if s]
    if valids:
        for sig in valids:
            msg = format_call(sig)
            send_to_discord(msg)
            send_to_telegram(msg)
            print(f"Sinyal dikirim: {sig['symbol']} - {sig['side']}")
    else:
        print("Tidak ada sinyal valid hari ini.")

job()
#schedule.every().day.at("02:00").do(job)  # 09:00 WIB
schedule.every(180).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
    
