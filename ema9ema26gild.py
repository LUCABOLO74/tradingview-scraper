#!/usr/bin/env python3
"""
Script per ottenere EMA9 e EMA26 di XAUUSD in real-time

Versione con diagnostica per ambienti CI:
- stampa diagnostica subito (flush=True)
- TEST_MODE / CI_TEST_MODE = "1" -> esegue una sola chiamata (utile per pipeline)
- SLEEP_SECONDS permette di ridurre l'attesa durante i test
"""

import os
import sys
import time
import logging
import traceback
from datetime import datetime

# Provo ad importare Indicators in modo robusto per mostrare eventuali errori d'import
try:
    from tradingview_scraper.symbols.technicals import Indicators
except Exception as e:
    # Stampa diagnostica dettagliata e esce con codice di errore così il CI fallisce visibilmente
    print("❌ Errore durante l'import di Indicators:", flush=True)
    traceback.print_exc()
    sys.exit(2)

# Configuro logging in modo che gli errori vengano mostrati nella console
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def normalize_timeframe(tf) -> str:
    """
    Normalizza valori comuni di timeframe nel formato atteso dalla libreria.
    """
    if tf is None:
        raise ValueError("Timeframe non valido: valore mancante")

    tf_orig = str(tf).strip()
    if not tf_orig:
        raise ValueError("Timeframe non valido: stringa vuota")

    # Gestione esplicita per '1M' (mese)
    if tf_orig == "1M":
        return "1M"

    tf_lower = tf_orig.lower()

    mapping = {
        # numerici comuni -> chiave
        "1": "1m",
        "3": "3m",
        "5": "5m",
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "120": "2h",
        "240": "4h",
        # già in notazione
        "1m": "1m",
        "3m": "3m",
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

    if tf_lower == "d":
        return "1d"
    if tf_lower == "w":
        return "1w"

    supported = ", ".join(["1m","3m","5m","15m","30m","1h","2h","4h","1d","1w","1M"])
    raise ValueError(f"Timeframe non supportato: {tf_orig}. Valori supportati: {supported}")

def get_ema_realtime_continuous(symbol="XAUUSD", exchange="OANDA", timeframe="1"):
    """
    Ottiene EMA9 e EMA26 in tempo reale e li stampa continuamente.
    Usa TEST_MODE/CI_TEST_MODE env var per eseguire solo una iterazione in CI.
    Usa SLEEP_SECONDS env var per cambiare il tempo di attesa (default 60).
    """
    # Informazioni di avvio (diagnostica)
    print("🚀 Avvio script ema9ema26gild.py", flush=True)
    print(f"  symbol={symbol}, exchange={exchange}, timeframe(input)={timeframe}", flush=True)

    # Normalizza il timeframe
    try:
        timeframe_normalized = normalize_timeframe(timeframe)
    except ValueError as e:
        print(f"❌ Timeframe non valido: {e}", flush=True)
        return

    # Inizializza lo scraper (avvolto in try/except per mostrare eventuali problemi)
    try:
        indicators_scraper = Indicators(export_result=False)
    except Exception:
        print("❌ Errore durante l'inizializzazione di Indicators:", flush=True)
        traceback.print_exc()
        return

    print("=" * 80, flush=True)
    print(f"🔄 Inizio streaming EMA9 e EMA26 per {symbol}", flush=True)
    print(f"Exchange: {exchange} | Timeframe: {timeframe_normalized}", flush=True)
    print("=" * 80, flush=True)
    print(flush=True)

    iteration = 0
    sleep_seconds = int(os.getenv("SLEEP_SECONDS", "60"))
    test_mode = os.getenv("TEST_MODE") == "1" or os.getenv("CI_TEST_MODE") == "1"

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
                    print(f"[{timestamp}] #{iteration}", flush=True)
                    print(f"  EMA9  : {ema9_str}", flush=True)
                    print(f"  EMA26 : {ema26_str}", flush=True)
                    print(f"  Diff  : {diff_str} {signal}", flush=True)
                    print("-" * 80, flush=True)

                else:
                    print(f"[{timestamp}] ❌ Errore: Scraping fallito", flush=True)
                    print(f"  Risposta: {result}", flush=True)
                    print("-" * 80, flush=True)

            except Exception:
                print(f"[{timestamp}] ❌ Eccezione durante lo scraping:", flush=True)
                traceback.print_exc()
                print("-" * 80, flush=True)

            # Se in TEST_MODE, eseguo solo una iterazione e poi esco (utile per CI)
            if test_mode:
                print("🧪 TEST_MODE attivo: esco dopo la prima iterazione.", flush=True)
                break

            # Attendi prima del prossimo aggiornamento
            print(f"⏳ Prossimo aggiornamento tra {sleep_seconds} secondi...\n", flush=True)
            time.sleep(sleep_seconds)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80, flush=True)
        print("❌ Streaming interrotto dall'utente", flush=True)
        print(f"Total iterazioni: {iteration}", flush=True)
        print("=" * 80, flush=True)

def get_ema_once(symbol="XAUUSD", exchange="OANDA", timeframe="1"):
    """
    Ottiene EMA9 e EMA26 una sola volta
    """
    print("📡 Esecuzione lettura singola", flush=True)
    try:
        timeframe_normalized = normalize_timeframe(timeframe)
    except ValueError as e:
        print(f"❌ Timeframe non valido: {e}", flush=True)
        return

    try:
        indicators_scraper = Indicators(export_result=False)
    except Exception:
        print("❌ Errore durante l'inizializzazione di Indicators:", flush=True)
        traceback.print_exc()
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 80, flush=True)
    print(f"📊 Lettura singola EMA9 e EMA26 per {symbol}", flush=True)
    print(f"Exchange: {exchange} | Timeframe: {timeframe_normalized}", flush=True)
    print("=" * 80, flush=True)

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

            print(f"\n[{timestamp}]", flush=True)
            print(f"  EMA9  : {ema9}", flush=True)
            print(f"  EMA26 : {ema26}", flush=True)
            print(f"\nDati completi: {data}", flush=True)
        else:
            print(f"❌ Errore: {result}", flush=True)

    except Exception:
        print(f"❌ Eccezione durante lo scraping:", flush=True)
        traceback.print_exc()

if __name__ == "__main__":
    # Comando diagnostico iniziale per capire se lo script parte in CI
    print("=== Eseguo come script principale ===", flush=True)
    print(f"PID={os.getpid()} PYTHONUNBUFFERED={os.getenv('PYTHONUNBUFFERED')} TEST_MODE={os.getenv('TEST_MODE')} CI_TEST_MODE={os.getenv('CI_TEST_MODE')}", flush=True)

    # Modalità: se TEST_MODE o CI_TEST_MODE è impostato a "1", eseguo get_ema_once per terminare velocemente
    if os.getenv("TEST_MODE") == "1" or os.getenv("CI_TEST_MODE") == "1":
        get_ema_once(symbol=os.getenv("SYMBOL", "XAUUSD"), exchange=os.getenv("EXCHANGE", "OANDA"), timeframe=os.getenv("TIMEFRAME", "1"))
    else:
        # Default: streaming continuo (se vuoi evitare il loop in CI imposta TEST_MODE=1)
        get_ema_realtime_continuous(symbol=os.getenv("SYMBOL", "XAUUSD"), exchange=os.getenv("EXCHANGE", "OANDA"), timeframe=os.getenv("TIMEFRAME", "1"))
