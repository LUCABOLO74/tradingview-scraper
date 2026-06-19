from tradingview_scraper.symbols.cal import CalendarScraper
from datetime import datetime, timedelta
import logging

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

def log_calendario_dividendi():
    try:
        log.info("=" * 80)
        log.info("CALENDARIO DIVIDENDI TRADINGVIEW - PROSSIMI 7 GIORNI - MERCATO USA")
        log.info("=" * 80)

        calendar_scraper = CalendarScraper()
        timestamp_now = datetime.now().timestamp()
        timestamp_in_7_days = (datetime.now() + timedelta(days=7)).timestamp()

        res = calendar_scraper.scrape_dividends(
            timestamp_now,
            timestamp_in_7_days,
            ["america"],
            values=["logoid", "name", "amount", "ex_date", "pay_date", "div_yield"]
        )

        if not res:
            log.info("Nessun dividendo trovato nel range richiesto.")
            return

        if isinstance(res, dict):
            records = res.get("data", [])
        else:
            records = res

        if not records:
            log.info("Nessun record dividendi disponibile.")
            return

        for i, item in enumerate(records, start=1):
            nome = item.get("name", "")
            logoid = item.get("logoid", "")
            amount = item.get("amount", "")
            ex_date = item.get("ex_date", "")
            pay_date = item.get("pay_date", "")
            div_yield = item.get("div_yield", "")

            log.info(
                f"[DIVIDENDO {i}] "
                f"name={nome} | "
                f"logoid={logoid} | "
                f"amount={amount} | "
                f"ex_date={ex_date} | "
                f"pay_date={pay_date} | "
                f"div_yield={div_yield}"
            )

        log.info(f"Totale record dividendi trovati: {len(records)}")
        log.info("=" * 80)

    except Exception as e:
        log.warning(f"Impossibile scaricare/loggare il calendario dividendi: {e}")


def main():
    log.info("=" * 80)
    log.info("LETTURA REPORT GIORNALIERO ORB 5M + COMPILAZIONE ORDINI ACTIVTRADER")
    log.info("=" * 80)

    log_calendario_dividendi()

    log.info("-" * 80)


if __name__ == "__main__":
    main()
