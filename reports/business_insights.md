# Business Insights Report — PakConnect Telecom (FICTIONAL)

> **Disclosure:** PakConnect Telecom is a fictional operator and **all data in this project is simulated** (Python, seed 42). These insights describe the *simulated* dataset only. They are not findings about Jazz, Zong, Ufone, Telenor or any real operator, and must never be quoted as real market results.
>
> Every number below was computed by `src/run_eda_and_kpis.py` from the cleaned data and stored in `reports/_kpi_results.json`. SQL totals reconcile exactly with these Python totals (see `src/test_sql_logic_sqlite.py`).

## Headline KPIs (Jan–Dec 2025, simulated)

| KPI | Value |
|---|---:|
| Total net service revenue (tax excluded) | PKR 158,009,345 |
| Total billed amount (incl. tax) | PKR 183,290,839 |
| Average monthly ARPU | PKR 1,458 |
| Subscribers: Jan opening → Dec closing | 8,762 → 9,191 (+429 net) |
| New subscribers (year) | 1,238 |
| Churn events (year) | 809 |

## The 10 Questions

### 1. Which month generated the highest revenue?
**Finding:** December 2025 — PKR 14,071,142. Lowest was February 2025 — PKR 12,355,968.
**Evidence:** Monthly revenue table in `_kpi_results.json`; chart `eda_01`.
**Implication:** Revenue is seasonal in this simulation (year-end peak, early-year dip) — a pattern built into the generation assumptions, so treat it as a hypothesis to test against real billing data, not as proven seasonality.
**Action:** Plan retention and upsell campaigns *before* the February-type dip, and protect network capacity for the December peak.

### 2. Which service category contributed the most revenue?
**Finding:** **Data** — PKR 75,562,115, about **47.1% of gross service revenue** (before discounts). Voice follows at 30.5%, VAS 17.3%, SMS only 5.2%.
**Implication:** This is a data-led business. SMS is commercially minor.
**Action:** Prioritise data-bundle design and data-network quality; stop spending promotional effort on SMS bundles except as retention add-ons.

### 3. Which city generated the highest revenue?
**Finding:** **Lahore** — PKR 41,194,570 (26.1% of net revenue), then Karachi PKR 37,446,199. Lowest: Quetta PKR 10,548,700.
**Implication:** Revenue follows subscriber scale (Lahore also has the most customers, 2,644 of 10,000).
**Action:** Lahore/Karachi are scale markets — compete on retention. Quetta's gap is a scale question first; check ARPU before assuming a pricing problem (see Q4).

### 4. Which city had the highest ARPU?
**Finding:** **Islamabad** — average monthly ARPU ≈ PKR 1,501, even though it ranks only 3rd in total revenue. Lowest ARPU: Quetta ≈ PKR 1,419. The spread is small (~5.8%).
**Implication:** Islamabad customers are the most valuable per head; Quetta's low revenue is mainly fewer subscribers, not dramatically weaker spend.
**Action:** Use Islamabad's package mix as the upsell template for other cities; grow Quetta by acquisition, not discounting.

### 5. Which package performed best?
**Finding:** By total revenue: **Family Connect** — PKR 36,554,291 (23.1%). By revenue per customer-month (package ARPU): **Business Pro** — PKR 4,190, far above Premium Max (PKR 2,978) and Family Connect (PKR 2,435). Weakest: Daily Saver (PKR 84 per customer-month) and Weekly Power (PKR 256).
**Implication:** Family Connect is the volume engine; Business Pro is the value engine. Daily/Weekly bundles barely monetise.
**Action:** Protect and expand Family Connect; create a migration path from Daily Saver → Weekly Power → Social Bundle/Smart Plus with first-upgrade incentives.

### 6. Did revenue growth align with subscriber growth?
**Finding:** Only partly. Revenue grew **+12.8%** from January (PKR 12,474,343) to December (PKR 14,071,142), while the subscriber base grew **+4.9%** (8,762 → 9,191). ARPU rose from PKR 1,421 to PKR 1,527 (+7.5%).
**Implication:** Growth was driven more by *more revenue per user* (mix + seasonality assumptions) than by acquisition.
**Action:** Report revenue growth and ARPU growth separately in management packs — conflating them hides whether growth is acquisition-led or wallet-led.

### 7. Which months had the highest churn?
**Finding:** **October 2025** — churn rate 0.96% of opening subscribers (88 churn events), followed by September (0.95%) and July (0.94%). Lowest: April (0.49%).
**Implication:** A late-Q3/Q4 churn bulge exists in the simulated data.
**Action:** Trigger save-offers and service-quality reviews in August–September, *before* the bulge, and interview churners from the peak months first when real data is available.

### 8. Which customer segments generated higher revenue?
**Finding:** By revenue per customer over the year: **Business PKR 36,762** ≫ Premium PKR 25,184 > Family PKR 19,696 > Mass PKR 8,066 > Student PKR 4,584. By total revenue, Business also leads (PKR 47,864,683) despite being only 13% of customers.
**Implication:** A small Business base carries a disproportionate share of revenue — concentration risk if business churn rises.
**Action:** Give Business accounts named account management and churn early-warning; treat Student as a future-value pipeline (graduate them into Smart Plus), not a current revenue source.

### 9. What opportunities exist to improve ARPU?
**Evidence-based opportunities:**
1. **Migrate Daily Saver / Weekly Power users upward** — combined they produce under PKR 2.82M/year at ARPU of PKR 84–256 (Q5).
2. **Replicate Islamabad's mix** (ARPU PKR 1,501) in Quetta and Multan (PKR 1,419–1,426) — even closing half the gap adds roughly PKR 40–50 per user-month in those cities (illustrative, from the ARPU gap × their average subscribers).
3. **Grow VAS attach** — VAS is already 17.3% of gross revenue and is concentrated in Business/Hybrid packages; extending VAS offers to Mass prepaid users is untested headroom in this dataset.
4. **Reduce discount leakage** — total discounts were PKR 2,572,419 (≈1.6% of gross); audit which segments receive discounts without retention benefit.

### 10. What should management consider?
1. Build the real version of this pipeline on actual billing data — the simulated model proves the *method* (grains, KPIs, reconciliation), not the market facts.
2. Adopt the KPI definitions in the README as the single source of truth (especially: ARPU uses **net service revenue**, never billed amount incl. tax).
3. Add churn-reason capture at cancellation — this dataset knows *when* customers churn, not *why*.
4. Review the Q3–Q4 churn bulge and the Daily/Weekly low-value tier at the next commercial meeting.
5. Keep tax reporting separate from service revenue in every pack (PKR 25,281,494 of tax passed through billing in this simulation).

## Known simulation artifacts (read before quoting any number)
- **December new subscribers = 0** is a generator artifact: 2025 join dates were generated only up to 30 November. December's net growth (−51) and its acquisition figures must **not** be interpreted as a real acquisition collapse. December revenue and ARPU are unaffected (they come from the active base).
- Monthly seasonality (Ramadan/Eid/year-end uplift) was an explicit modelling assumption, so "discovering" seasonality in the output is circular — it validates the generator, not the market.
- 965 customer-months (0.9%) sit above mean + 3 SD of net revenue. Validation shows they are legitimate high-value Business Pro / Premium records (no errors, no negatives), so they were **kept**, not deleted as "outliers".
