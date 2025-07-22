
import requests, time, schedule
from datetime import datetime

# Discord webhook untuk sinyal
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1396241698929119273/9rzJbZXVoEgBWEZk69njsnFJe_whzG9av58lwBewII9owdqiP7-F0uDvM7f_DZzrh1Al"

# Daftar pair yang dipantau
PAIRS = ['ETHUSDT', 'BTCUSDT', 'AAVEUSDT', 'DOGEUSDT', 'XRPUSDT', 'MATICUSDT', 'SUIUSDT', 'OPUSDT', 'HBARUSDT', 'PEPEUSDT', 'ARBUSDT', 'INJUSDT', 'RNDRUSDT', 'LINKUSDT', 'NEARUSDT', 'PENGUUSDT', 'SEIUSDT', '1000FLOKIUSDT', '1000BONKUSDT', 'WIFUSDT', 'TIAUSDT', 'BLURUSDT', 'IDUSDT', 'ORDIUSDT', 'LDOUSDT', 'FETUSDT', 'JUPUSDT', 'NOTUSDT', 'STRKUSDT']

# Endpoint API Bitunix
API = "https://fapi.bitunix.com/api/v1/futures/market/kline"

def get_klines(symbol, interval="1h", limit=50):
    try:
        r = requests.get(API, params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=10)
        d = r.json()
        if d.get("code") == 0 and isinstance(d.get("data"), list):
            return d["data"]
    except:
        pass
    return []

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
            tp = last + (last - sl)
            tp2 = last + 2 * (last - sl)
            tp3 = last + 3 * (last - sl)
            sl = swing_low
            rr = abs(tp - last) / abs(last - sl)
            return format_signal(symbol, "LONG", last, sl, tp, rr)
        elif broke_down and last < swing_low:
            tp = last - (sl - last)
            tp2 = last - 2 * (sl - last)
            tp3 = last - 3 * (sl - last)
            sl = swing_high
            rr = abs(last - tp) / abs(sl - last)
            return format_signal(symbol, "SHORT", last, sl, tp, rr)
    except:
        pass
    return None

def format_signal(symbol, side, entry, sl, tp, rr):
    lot = 0.1
    risk = 100
    reward = risk * rr
    conf = "HIGH" if rr > 2.0 else "MED" if rr > 1.2 else "LOW"
    return f"""
🔥 MASTER CALL: {symbol.replace("USDT", "/USD")} - {side}

📍 Entry: {entry}
🛑 Stop Loss: {sl}
🎯 Take Profit: TP1: {tp} TP2: {tp2} TP3: {tp3}
📊 Risk Reward: 1:{int(rr)}
🔻 Risk per Trade: ~${risk}
🎯 Reward Target: ~${reward}
✅ Confidence Level: {conf}
"""

def send_to_discord(text):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": text})
    except:
        pass

def job():
    print("🔎 Menganalisis...")
    for pair in PAIRS:
        signal = detect_smc_signal(pair)
        if signal:
            send_to_discord(signal)
            print(f"✅ Sinyal dikirim: {pair}")
        else:
            print(f"❌ Tidak ada sinyal valid untuk {pair}")

# Schedule setiap 3 jam (180 menit)
schedule.every(180).minutes.do(job)

# Eksekusi awal
job()

while True:
    schedule.run_pending()
    time.sleep(60)
