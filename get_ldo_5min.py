import json
from datetime import datetime
from zoneinfo import ZoneInfo

from tradingview_scraper.symbols.stream.price import RealTimeData


SYMBOL = "MIL:LDO"
TZ = ZoneInfo("Europe/Rome")


def format_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=TZ).strftime("%Y-%m-%d; %H:%M")


def parse_first_5_bars_last_day():
    rt = RealTimeData()
    stream = rt.get_ohlcv(SYMBOL)

    for packet in stream:
        if packet.get("m") != "timescale_update":
            continue

        payload = packet.get("p", [])
        if len(payload) < 2:
            continue

        series_block = payload[1].get("sds_1", {})
        bars = series_block.get("s", [])
        if not bars:
            continue

        parsed = []
        for bar in bars:
            values = bar.get("v", [])
            if len(values) < 6:
                continue

            ts, op, hi, lo, cl, vol = values[:6]
            dt = datetime.fromtimestamp(ts, tz=TZ)

            parsed.append(
                {
                    "timestamp": ts,
                    "dt": dt,
                    "day": dt.strftime("%Y-%m-%d"),
                    "open": float(op),
                    "high": float(hi),
                    "low": float(lo),
                    "close": float(cl),
                    "volume": float(vol),
                }
            )

        if not parsed:
            continue

        last_day = max(x["day"] for x in parsed)
        first_5 = [x for x in parsed if x["day"] == last_day][:5]

        if len(first_5) < 5:
            raise RuntimeError(f"Trovate solo {len(first_5)} candele per l'ultimo giorno disponibile")

        return first_5

    raise RuntimeError("Nessun pacchetto timescale_update trovato nello stream")


def aggregate_5m(bars):
    return {
        "timestamp": bars[0]["timestamp"],
        "reference_time": format_ts(bars[0]["timestamp"]),
        "open": bars[0]["open"],
        "high": max(x["high"] for x in bars),
        "low": min(x["low"] for x in bars),
        "close": bars[-1]["close"],
        "volume": sum(x["volume"] for x in bars),
    }


def main():
    first_5 = parse_first_5_bars_last_day()
    candle_5m = aggregate_5m(first_5)

    print("SYMBOL:", SYMBOL)
    print("ULTIMO GIORNO DISPONIBILE:", first_5[0]["day"])
    print("PRIME 5 CANDELE 1 MIN:")

    for bar in first_5:
        print(
            json.dumps(
                {
                    "timestamp": format_ts(bar["timestamp"]),
                    "open": bar["open"],
                    "high": bar["high"],
                    "low": bar["low"],
                    "close": bar["close"],
                    "volume": bar["volume"],
                },
                ensure_ascii=False,
            )
        )

    print("CANDELA 5 MIN AGGREGATA:")
    print(
        json.dumps(
            candle_5m,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
