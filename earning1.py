from tradingview_scraper.symbols.cal import CalendarScraper

calendar_scraper = CalendarScraper()

# Scrape earnings from all markets.
res = calendar_scraper.scrape_earnings(
  values=["logoid", "name", "earnings_per_share_fq"]
)


# Scrape upcoming week earnings from the american market
from datetime import datetime, timedelta

timestamp_now = datetime.now().timestamp()
timestamp_in_7_days = (datetime.now() + timedelta(days=7)).timestamp()

res = calendar_scraper.scrape_earnings(
  timestamp_now,
  timestamp_in_7_days,
  ["america"],
  values=["logoid", "name", "earnings_per_share_fq"]
  )
