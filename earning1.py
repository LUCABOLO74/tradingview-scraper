from tradingview_scraper.symbols.cal import CalendarScraper
from datetime import datetime, timedelta
import logging

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

def log_calendario_earnings():
    print("log")
    try:
        log.info("=" * 80)
        log.info("CALENDARIO EARNINGS TRADINGVIEW - PROSSIMI 7 GIORNI - MERCATO USA")
        log.info("=" * 80)
        print("inizio. calendar")
        calendar_scraper = CalendarScraper()
        print("fine calendar")
        timestamp_now = datetime.now().timestamp()
        timestamp_in_7_days = (datetime.now() + timedelta(days=7)).timestamp()

        res = calendar_scraper.scrape_earnings(
            timestamp_now,
            timestamp_in_7_days,
            ["america"],
            values=["logoid", "name", "earnings_per_share_fq"]
        )
        print(res)
        if not res:
            log.info("Nessun earnings trovato nel range richiesto.")
            return

        if isinstance(res, dict):
            records = res.get("data", [])
        else:
            records = res

        if not records:
            log.info("Nessun record earnings disponibile.")
            return

        for i, item in enumerate(records, start=1):
            nome = item.get("name", "")
            logoid = item.get("logoid", "")
            eps = item.get("earnings_per_share_fq", "")

            log.info(
                f"[EARNINGS {i}] "
                f"name={nome} | "
                f"logoid={logoid} | "
                f"earnings_per_share_fq={eps}"
            )

        log.info(f"Totale record earnings trovati: {len(records)}")
        log.info("=" * 80)

    except Exception as e:
        log.warning(f"Impossibile scaricare/loggare il calendario earnings: {e}")
def main():
    print("main")
    log.info("=" * 80)
    log.info("LETTURA REPORT GIORNALIERO ORB 5M + COMPILAZIONE ORDINI ACTIVTRADER")
    log.info("=" * 80)

    log_calendario_earnings()

    #report_path = find_latest_orb_report()
    #ordini = parse_report_rows(report_path)

    #if not ordini:
        #log.info("Nessun ordine valido da inviare.")
        #return

    #risultati = asyncio.run(esegui_ordini_da_lista(ordini))
    #salva_risultati(risultati, Config.OUTPUT_REPORT)

    #ok_count = sum(1 for r in risultati if r["ok"])
    #ko_count = len(risultati) - ok_count

    log.info("-" * 80)
    #log.info(f"Totale ordini elaborati: {len(risultati)}")
    #log.info(f"Ordini compilati correttamente: {ok_count}")
    #log.info(f"Ordini con errore: {ko_count}")
    #log.info("-" * 80)
 
if __name__ == "__main__":
    main()
