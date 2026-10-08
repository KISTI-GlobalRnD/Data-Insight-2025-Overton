# Public reproducibility materials for the Overton × OpenAlex report

## Public scope

These materials correspond to the manuscript publication date 2025-12-31 and run tag 20251026. They provide public aggregate tables, a headline-value verification script, report and figure-generation code, and an environment list.

Licensed Overton source data and derived policy-document or article-level records are not included. The public materials therefore support the following tasks:

- recompute the report's headline observations and linked-sample composition expected shares;
- inspect the public aggregate tables and report-generation code; and
- audit tables and figures that use the same public aggregates.

A complete rebuild from source records requires separate Overton access and the local inputs listed in the report runbook.

## Quick verification

Extract the code and aggregate archives into the same directory, then run:

```bash
python scripts/verify_public_report_aggregates.py --root . --run-tag 20251026
```

The script recomputes the two Korea-related citation directions, the social- and health-science shares, the source-type composition and within-source-type components of Korea's social-science gap, the combined KDI-KIEP share, the think-tank shares in both directions, Korea's rank in the 11-country field-gap comparison, think-tank citation shares and within-type institution concentration across those countries, the country count and social-science range of the 25 foreign KDI/KIEP citation-profile matches, and the 36.1% U.S. linked-sample composition expected share. It also verifies country-assignment missingness and mechanical bounds, field-gap weighting sensitivity, institution document and citation density, baseline author-country sensitivity counts, and the recorded cache provenance. A successful run prints `PUBLIC_AGGREGATE_VERIFICATION=PASS`, meaning the public aggregate values and calculation relationships passed—not that licensed source data or the upstream Overton export universe were recreated.

## File versioning

`REPRODUCIBILITY_MANIFEST.json` records paths, sizes, SHA-256 values, the execution environment, the country-assignment rule, and the source metadata for the country-domain cache. `SHA256SUMS.txt` identifies the exact archive files. These checksums identify the distributed version independently of a Git commit.
