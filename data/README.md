# Data provenance

- Publisher on Kaggle: Sakshi Goyal.
- Dataset: [Credit Card Customers](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers).
- Download endpoint: `https://www.kaggle.com/api/v1/datasets/download/sakshigoyal7/credit-card-customers`.
- Retrieved for this project: 2026-11-05 (UTC).
- Pinned file: `raw/BankChurners.csv`, 1,510,880 bytes, 10,127 rows, 23 columns.
- SHA-256: `c91b525a2a6755a1b0b80dad1d0d008ca97ec4df34552c8f47ffa12b6184b779`.
- Kaggle lists the license as **CC0: Public Domain**. The raw CSV is redistributed under the source's listed terms, separately from the project's MIT code license.
- The uploader attributes the data to Analyttica's LEAPS platform. A named source bank, collection method, geography, snapshot dates, currency, and whether the records are synthetic are **not independently verified**. Do not describe this as confirmed real-bank or Vietnamese banking data.

The CSV is committed so a recruiter can reproduce results offline. `scripts/download_data.py` can fetch and verify the same bytes. If a future Kaggle version changes, the checksum check deliberately fails; review a new version before updating the pin.

The source has no blank cells or duplicate customer identifiers. It does contain `Unknown` categories: 1,519 education, 749 marital status, and 1,112 income entries. These are retained, not guessed or dropped. Two `Naive_Bayes_Classifier_*` columns are source model outputs; neither is used in analysis, rules, or the dashboard.

`data/processed/retention.sqlite` is rebuilt locally and ignored by Git. The HTML embeds a subset of anonymized behavior attributes and filter labels, with no customer IDs. No rows are generated or altered to manufacture an insight.
