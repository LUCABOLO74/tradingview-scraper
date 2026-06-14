import json
from datetime import datetime
from zoneinfo import ZoneInfo

from tradingview_scraper.symbols.stream.streamer import Streamer

SYMBOL = "MIL:LDO"
TZ = ZoneInfo("Europe/Rome")


def fmt(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=TZ).strftime("%Y-%m-%d; %H:%M")


def normalize_bar(values):
    ts, op, hi, lo, cl, vol = values[:6]
    dt = datetime.fromtimestamp(ts, tz=TZ)
    return {
        "timestamp": float(ts),
        "dt": dt,
        "day": dt.strftime("%Y-%m-%d"),
        "hm": dt.strftime("%H:%M"),
        "open": float(op),
        "high": float(hi),
        "low": float(lo),
        "close": float(cl),
        "volume": float(vol),
    }


def extract_bars_from_result(result):
    bars = []

    if isinstance(result, dict):
        for _, value in result.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "v" in item and len(item["v"]) >= 6:
                        bars.append(normalize_bar(item["v"]))

    return bars


def load_historical_bars():
    streamer = Streamer(export_result=True, export_type="json")
    result = streamer.stream(symbol=SYMBOL)
    bars = extract_bars_from_result(result)

    if not bars:
        raise RuntimeError("Nessuna barra storica trovata con Streamer")

    return sorted(bars, key=lambda x: x["timestamp"])


def get_opening_5_bars(bars):
    last_day = max(x["day"] for x in bars)
    target_times = ["09:00", "09:01", "09:02", "09:03", "09:04"]

    same_day = [x for x in bars if x["day"] == last_day]
    by_time = {x["hm"]: x for x in same_day}

    missing = [t for t in target_times if t not in by_time]
    if missing:
        raise RuntimeError(f"Barre mancanti per {last_day}: {', '.join(missing)}")

    selected = [by_time[t] for t in target_times]
    return last_day, selected


def aggregate_5m(last_day, bars_1m):
    return {
        "timestamp": bars_1m[0]["timestamp"],
        "reference_time": f"{last_day}; 09:05",
        "open": bars_1m[0]["open"],
        "high": max(x["high"] for x in bars_1m),
        "low": min(x["low"] for x in bars_1m),
        "close": bars_1m[-1]["close"],
        "volume": sum(x["volume"] for x in bars_1m),
    }


def main():
    bars = load_historical_bars()
    last_day, bars_1m = get_opening_5_bars(bars)
    candle_5m = aggregate_5m(last_day, bars_1m)

    print("SYMBOL:", SYMBOL)
    print("GIORNO DI RIFERIMENTO:", last_day)
    print("CANDELE 1 MIN USATE (09:00-09:04):")

    for bar in bars_1m:
        print(json.dumps({
            "timestamp": fmt(bar["timestamp"]),
            "open": bar["open"],
            "high": bar["high"],
            "low": bar["low"],
            "close": bar["close"],
            "volume": bar["volume"],
        }, ensure_ascii=False))

    print("CANDELA 5 MIN AGGREGATA:")
    print(json.dumps(candle_5m, ensure_ascii=False))


if __name__ == "__main__":
    main()
