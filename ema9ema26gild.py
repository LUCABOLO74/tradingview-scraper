#!/usr/bin/env python3
"""
Script per ottenere EMA9 e EMA26 di XAUUSD in real-time
Aggiornamento continuo con stampa a video

Questa versione normalizza i timeframe (es. "1", "60", "1m", "1h", "1M") prima di passare
alla classe Indicators che richiede chiavi come "1m","5m","15m","30m","1h","2h","4h","1d","1w","1M".
"""

import time
from datetime import datetime
from tradingview_scraper.symbols.technicals import Indicators

def normalize_timeframe(tf) -> str:
    """
    Normalizza valori comuni di timeframe nel formato atteso dalla libreria.

    Accetta:
      - numeri in stringa: "1","5","15","30","60","120","240"
      - notazioni con unità: "1m","5m","15m","30m","1h","2h","4h","1d","1w","1M"
      - la specifica "1M" (mese) viene resa esattamente "1M"
    Restituisce:
      - una stringa corrispondente a una chiave valida: "1m","5m","15m","30m","1h","2h","4h","1d","1w","1M"
    Lancia:
      - ValueError se il timeframe non è supportato.
    """
    if tf is None:
        raise ValueError("Timeframe non valido: valore mancante")

    tf_orig = str(tf).strip()
    if not tf_orig:
        raise ValueError("Timeframe non valido: stringa vuota")

    # Gestione esplicita per '1M' (mese) per evitare collisione con '1m' (minuto)
    if tf_orig == "1M":
        return "1M"

    tf_lower = tf_orig.lower()

    mapping = {
        # numerici comuni -> chiave
        "1": "1m",
        "5": "5m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        # già in notazione
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "2h": "2h",
        "4h": "4h",
        "1d": "1d",
        "1w": "1w",
        # varianti mese -> 1M
        "1mo": "1M",
        "1mon": "1M",
        "1month": "1M",
        "month": "1M",
    }

    if tf_lower in mapping:
        return mapping[tf_lower]

    # supporta anche "d", "w" (senza numero) come alias per 1d e 1w
    if tf_lower == "d":
        return "1d"
    if tf_lower == "w":
        return "1w"

    supported = ", ".join(["1m","5m","15m","30m","1h","2h","4h","1d","1w","1M"])
    raise ValueError(f"Timeframe non supportato: {tf_orig}. Valori supportati: {supported}")

def get_ema_realtime_continuous(symbol="XAUUSD", exchange="OANDA", timeframe="1"):
    """
    Ottiene EMA9 e EMA26 in tempo reale e li stampa continuamente

    Args:
        symbol: Simbolo del titolo (default: XAUUSD)
        exchange: Exchange (default: OANDA per l'oro)
        timeframe: Timeframe in formato utente (es. "1", "1m", "1h", "1M")
    """
    # Normalizza il timeframe prima di inizializzare lo scraping
    try:
        timeframe_normalized = normalize_timeframe(timeframe)
    except ValueError as e:
        print(f"❌ Timeframe non valido: {e}")
        return

    # Inizializza lo scraper
    indicators_scraper = Indicators(export_result=False)

    print("=" * 80)
    print(f"🔄 Inizio streaming EMA9 e EMA26 per {symbol}")
    print(f"Exchange: {exchange} | Timeframe: {timeframe_normalized}")
    print("=" * 80)
    print()

    iteration = 0

    try:
        while True:
            iteration += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                # Scrape gli indicatori
                result = indicators_scraper.scrape(
                    exchange=exchange,
                    symbol=symbol,
                    timeframe=timeframe_normalized,
                    indicators=["EMA9", "EMA26"],
                    allIndicators=False
                )

                # Verificare se lo scraping è riuscito
                if result.get('status') == 'success':
                    data = result.get('data', {})

                    ema9 = data.get('EMA9', 'N/A')
                    ema26 = data.get('EMA26', 'N/A')

                    # Formattare i valori
                    ema9_str = f"{ema9:.2f}" if isinstance(ema9, (int, float)) else ema9
                    ema26_str = f"{ema26:.2f}" if isinstance(ema26, (int, float)) else ema26

                    # Calcolare la differenza (signal)
                    if isinstance(ema9, (int, float)) and isinstance(ema26, (int, float)):
                        diff = ema9 - ema26
                        diff_str = f"{diff:+.2f}"
                        signal = "🟢 BUY" if diff > 0 else "🔴 SELL" if diff < 0 else "⚪ NEUTRAL"
                    else:
                        diff_str = "N/A"
                        signal = "⚪ NEUTRAL"

                    # Stampa i risultati
                    print(f"[{timestamp}] #{iteration}")
                    print(f"  EMA9  : {ema9_str}")
                    print(f"  EMA26 : {ema26_str}")
                    print(f"  Diff  : {diff_str} {signal}")
                    print("-" * 80)

                else:
                    print(f"[{timestamp}] ❌ Errore: Scraping fallito")
                    print(f"  Risposta: {result}")
                    print("-" * 80)

            except Exception as e:
                print(f"[{timestamp}] ❌ Eccezione: {str(e)}")
                print("-" * 80)

            # Attendi 60 secondi prima del prossimo aggiornamento
            print(f"⏳ Prossimo aggiornamento tra 60 secondi...\n")
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("❌ Streaming interrotto dall'utente")
        print(f"Total iterazioni: {iteration}")
        print("=" * 80)


def get_ema_once(symbol="XAUUSD", exchange="OANDA", timeframe="1"):
    """
    Ottiene EMA9 e EMA26 una sola volta

    Args:
        symbol: Simbolo del titolo
        exchange: Exchange
        timeframe: Timeframe in formato utente (es. "1", "1m", "1h", "1M")
    """
    try:
        timeframe_normalized = normalize_timeframe(timeframe)
    except ValueError as e:
        print(f"❌ Timeframe non valido: {e}")
        return

    indicators_scraper = Indicators(export_result=False)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 80)
    print(f"📊 Lettura singola EMA9 e EMA26 per {symbol}")
    print(f"Exchange: {exchange} | Timeframe: {timeframe_normalized}")
    print("=" * 80)

    try:
        result = indicators_scraper.scrape(
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe_normalized,
            indicators=["EMA9", "EMA26"],
            allIndicators=False
        )

        if result.get('status') == 'success':
            data = result.get('data', {})

            ema9 = data.get('EMA9', 'N/A')
            ema26 = data.get('EMA26', 'N/A')

            print(f"\n[{timestamp}]")
            print(f"  EMA9  : {ema9}")
            print(f"  EMA26 : {ema26}")
            print(f"\nDati completi: {data}")
        else:
            print(f"❌ Errore: {result}")

    except Exception as e:
        print(f"❌ Eccezione: {str(e)}")


if __name__ == "__main__":
    # OPZIONE 1: Streaming continuo (uncommentare per usare)
    # ========================================================
    # Puoi passare "1" (compatibilità), "1m", "1h", "1M" ecc.
    get_ema_realtime_continuous(symbol="XAUUSD", exchange="OANDA", timeframe="1")

    # OPZIONE 2: Lettura singola (uncommentare per usare)
    # ========================================================
    # get_ema_once(symbol="XAUUSD", exchange="OANDA", timeframe="1")
