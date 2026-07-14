#!/usr/bin/env python3
"""
Script per ottenere EMA9 e EMA26 di XAUUSD in real-time
Aggiornamento continuo con stampa a video
"""

import time
from datetime import datetime
from tradingview_scraper.symbols.technicals import Indicators

def get_ema_realtime_continuous(symbol="XAUUSD", exchange="OANDA", timeframe="1"):
    """
    Ottiene EMA9 e EMA26 in tempo reale e li stampa continuamente
    
    Args:
        symbol: Simbolo del titolo (default: XAUUSD)
        exchange: Exchange (default: OANDA per l'oro)
        timeframe: Timeframe (1 = 1 minuto)
    """
    
    # Inizializza lo scraper
    indicators_scraper = Indicators(export_result=False)
    
    print("=" * 80)
    print(f"🔄 Inizio streaming EMA9 e EMA26 per {symbol}")
    print(f"Exchange: {exchange} | Timeframe: {timeframe} minuto")
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
                    timeframe=timeframe,
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
        timeframe: Timeframe
    """
    
    indicators_scraper = Indicators(export_result=False)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 80)
    print(f"📊 Lettura singola EMA9 e EMA26 per {symbol}")
    print(f"Exchange: {exchange} | Timeframe: {timeframe} minuto")
    print("=" * 80)
    
    try:
        result = indicators_scraper.scrape(
            exchange=exchange,
            symbol=symbol,
            timeframe=timeframe,
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
    get_ema_realtime_continuous(symbol="XAUUSD", exchange="OANDA", timeframe="1")
    
    # OPZIONE 2: Lettura singola (uncommentare per usare)
    # ========================================================
    # get_ema_once(symbol="XAUUSD", exchange="OANDA", timeframe="1")