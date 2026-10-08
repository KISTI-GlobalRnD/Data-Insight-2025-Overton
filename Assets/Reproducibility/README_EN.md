# Public reproducibility materials for the Overton × OpenAlex report

## Public scope

These materials correspond to the manuscript publication date 2025-12-31 and run tag 20251026. They provide public aggregate tables, a headline-value verification script, report and figure-generation code, and an environment list.

Licensed Overton source data and derived policy-document or article-level records are not included. The public materials therefore support the following tasks:

- recompute the report's headline observations and expected shares based on the linked sample;
- inspect the public aggregate tables and report-generation code; and
- audit tables and figures that use the same public aggregates.

A complete rebuild from source records requires separate Overton access and the local inputs listed in the report runbook.

## Quick verification

Extract the code and aggregate archives into the same directory, then run:

```bash
python scripts/verify_public_report_aggregates.py --root . --run-tag 20251026
```

The script recomputes the two citation directions involving Korea and their social- and health-science shares. It checks the components of the social-science gap, the combined KDI-KIEP share, think-tank shares, and country comparisons. It also checks the country count and social-science range of the 25 foreign institutions with the most similar citation profiles, and the 36.1% U.S. expected share based on the linked sample.

Further checks cover missing country information, mechanical bounds, alternative weighting methods, institutional citation and document counts, author-country sensitivity counts, and the recorded source metadata. A successful run prints `PUBLIC_AGGREGATE_VERIFICATION=PASS`. This confirms the public aggregate values and calculations; it does not reproduce licensed source data or the original Overton export selection.

## File versioning

`REPRODUCIBILITY_MANIFEST.json` records paths, sizes, SHA-256 values, the execution environment, the country-assignment rule, and the source metadata for the country-domain cache. `SHA256SUMS.txt` identifies the exact archive files. These checksums identify the distributed version independently of a Git commit.
