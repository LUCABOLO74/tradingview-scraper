name: Run ema9ema26gold

on:
  workflow_dispatch:

jobs:
  run-script:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install package
        run: |
          pip install --upgrade pip
          pip install tradingview-scraper

      - name: Run script
        run: python ema9ema26gold.py
