#!/usr/bin/env python3
"""Build isolated October 2026 web aggregates; preserve the print inputs/assets."""
from pathlib import Path
import argparse
import hashlib
import json
import time

import duckdb

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "local_runs/overton20261004_oa20260625_online"
RAW = Path("/hdd/Data/Overton/parsed/20261004")
MAPPING = STAGE / "doi_openalex.parquet"
PUBLIC = ROOT / "Data_Insight/Assets/Reproducibility/update_202610"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare-only", action="store_true")
    args = ap.parse_args()
    STAGE.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(STAGE / "analysis.duckdb"))
    con.execute("SET threads=4")
    con.execute("SET memory_limit='12GB'")
    con.execute("SET enable_progress_bar=false")
    con.execute(f"SET temp_directory='{STAGE}/duckdb_tmp'")
    source_paths = [MAPPING, *[RAW/f'{prefix}__Overton_20261004_raw__{suffix}.parquet' for prefix,suffix in
                             [('01','MAIN'),('09','SUB__policy_source_country'),('10','SUB__policy_source_type'),('12','SUB__dois_cited')]]]
    identity = {p.name:{'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in source_paths}
    contract = STAGE/'input_contract.json'
    if contract.exists():
        assert json.loads(contract.read_text()) == identity, 'Inputs changed; use a new analysis stage'
    else:
        contract.write_text(json.dumps(identity,indent=2)+'\n')

    def table(name, sql):
        if not con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name=?", [name]).fetchone()[0]:
            print(f"build {name}", flush=True)
            con.execute(f"CREATE TABLE {name} AS {sql}")

    def csv(name, sql):
        con.execute(f"COPY ({sql}) TO '{PUBLIC}/{name}.csv' (HEADER, DELIMITER ',')")

    table("doi_map", f"SELECT DISTINCT doi,oaid_w,publication_year FROM '{MAPPING}'")
    table("doi_quality", "SELECT doi,count(DISTINCT oaid_w) n_works FROM doi_map GROUP BY doi")
    normalize = r"lower(regexp_replace(trim(dois_cited),'[\p{Cf}\s]','','g'))"
    table("raw_pairs", f"SELECT DISTINCT policy_document_id,{normalize} AS doi FROM '{RAW}/12__Overton_20261004_raw__SUB__dois_cited.parquet' WHERE policy_document_id IS NOT NULL AND dois_cited IS NOT NULL AND {normalize}<>''")
    table("citations_all", "SELECT DISTINCT r.policy_document_id,m.oaid_w FROM raw_pairs r JOIN doi_map m USING(doi)")
    table("citations", "SELECT DISTINCT r.policy_document_id,m.oaid_w FROM raw_pairs r JOIN doi_map m USING(doi) JOIN doi_quality q USING(doi) WHERE q.n_works=1")
    table("pc", f"SELECT DISTINCT policy_document_id,trim(split_part(policy_source_country,' > ',1)) AS country FROM '{RAW}/09__Overton_20261004_raw__SUB__policy_source_country.parquet' WHERE policy_source_country IS NOT NULL AND trim(policy_source_country)<>''")
    table("pt", f"SELECT DISTINCT policy_document_id,trim(split_part(policy_source_type,' > ',1)) AS source_type FROM '{RAW}/10__Overton_20261004_raw__SUB__policy_source_type.parquet' WHERE policy_source_type IS NOT NULL AND trim(policy_source_type)<>''")
    table("policy", f"SELECT DISTINCT policy_document_id,policy_source_id,policy_source_title,published_on FROM '{RAW}/01__Overton_20261004_raw__MAIN.parquet'")
    csv("doi_linkage_audit", """SELECT
        (SELECT count(*) FROM policy) raw_policy_documents,
        (SELECT count(*) FROM raw_pairs) unique_document_doi_pairs,
        (SELECT count(DISTINCT doi) FROM raw_pairs) unique_dois,
        (SELECT count(*) FROM doi_quality) matched_dois,
        (SELECT count(*) FROM doi_quality WHERE n_works=1) unambiguous_dois,
        (SELECT count(*) FROM doi_quality WHERE n_works>1) ambiguous_dois,
        (SELECT count(*) FROM raw_pairs JOIN doi_quality USING(doi) WHERE n_works>1) ambiguous_document_doi_pairs,
        (SELECT count(*) FROM citations) included_document_work_pairs,
        (SELECT count(*) FROM citations_all) all_mapping_document_work_pairs""")
    print(con.execute(f"SELECT * FROM '{PUBLIC}/doi_linkage_audit.csv'").df().to_string(index=False), flush=True)
    if args.prepare_only:
        return
    complete = json.loads((STAGE / "extraction_complete.json").read_text())
    done = list((STAGE / "enrichment").glob("*.done.json"))
    assert len(done) == complete["chunks"], "Enrichment is incomplete"
    missing = con.execute(f"SELECT count(*) FROM (SELECT DISTINCT oaid_w FROM doi_map EXCEPT SELECT DISTINCT oaid_w FROM '{STAGE}/enrichment/oa_*.parquet')").fetchone()[0]
    assert missing == 0, 'Current mapping has works without enrichment'
    table("works", f"""WITH ror AS (
        SELECT oaid_w,ror_country country,sum(row_count) n
        FROM '{STAGE}/enrichment/country_*.parquet'
        WHERE regexp_full_match(ror_country,'[A-Z]{{2}}') GROUP BY 1,2),
        ranked AS (SELECT *,row_number() OVER(PARTITION BY oaid_w ORDER BY n DESC,country) rn FROM ror),
        fallback AS (SELECT oaid_w,min(institution_country) country
          FROM '{STAGE}/enrichment/country_*.parquet'
          WHERE regexp_full_match(institution_country,'[A-Z]{{2}}')
          GROUP BY 1 HAVING count(DISTINCT institution_country)=1),
        ties AS (SELECT r.oaid_w,count(*) n FROM ror r JOIN ranked m
          ON r.oaid_w=m.oaid_w AND m.rn=1 AND r.n=m.n GROUP BY 1),
        meta AS (SELECT oaid_w,max(publication_year) pubyear FROM doi_map GROUP BY 1),
        oa AS (SELECT oaid_w,max(is_oa) is_oa FROM '{STAGE}/enrichment/oa_*.parquet' GROUP BY 1)
        SELECT meta.*,oa.is_oa,coalesce(m.country,f.country) country,
          m.country ror_country,coalesce(t.n>1,false) ror_mode_tied,
          CASE WHEN m.country IS NOT NULL THEN 'ror_mode'
               WHEN f.country IS NOT NULL THEN 'institution_single' ELSE 'unresolved' END country_assignment_stage
        FROM meta LEFT JOIN ranked m ON meta.oaid_w=m.oaid_w AND m.rn=1
        LEFT JOIN fallback f ON meta.oaid_w=f.oaid_w
        LEFT JOIN ties t ON meta.oaid_w=t.oaid_w LEFT JOIN oa ON meta.oaid_w=oa.oaid_w""")
    table("topics", f"SELECT DISTINCT t.oaid_w,l.topic_id,l.topic,l.domain,l.field,l.subfield FROM '{STAGE}/enrichment/topics_*.parquet' t JOIN '{STAGE}/topic_lookup.parquet' l USING(topic_id)")
    table("wd", "SELECT DISTINCT oaid_w,domain FROM topics WHERE domain IS NOT NULL AND domain<>''")
    table("repeat", "SELECT oaid_w,count(*) n FROM citations GROUP BY 1")
    table("flow", "SELECT pc.country policy_country,w.country research_country,count(*) citation_rows FROM citations c JOIN pc USING(policy_document_id) LEFT JOIN works w USING(oaid_w) GROUP BY 1,2")
    csv("data_profile", """SELECT 'document_work_pairs' indicator,count(*) AS "value" FROM citations
        UNION ALL SELECT 'citing_policy_documents',count(DISTINCT policy_document_id) FROM citations
        UNION ALL SELECT 'cited_works',count(DISTINCT oaid_w) FROM citations
        UNION ALL SELECT 'works_cited_at_least_twice',count(*) FROM repeat WHERE n>=2
        UNION ALL SELECT 'korean_policy_documents',count(DISTINCT policy_document_id) FROM citations JOIN pc USING(policy_document_id) WHERE pc.country='South Korea'
        UNION ALL SELECT 'korean_policy_citations',count(*) FROM citations JOIN pc USING(policy_document_id) WHERE pc.country='South Korea'
        UNION ALL SELECT 'citations_to_korean_research',count(*) FROM citations JOIN works USING(oaid_w) WHERE works.country='KR'
        UNION ALL SELECT 'citations_without_research_country',count(*) FROM citations JOIN works USING(oaid_w) WHERE works.country IS NULL
        UNION ALL SELECT 'citations_without_domain',count(*) FROM citations c WHERE NOT EXISTS(SELECT 1 FROM wd WHERE wd.oaid_w=c.oaid_w)""")
    csv("policy_research_flow", "SELECT * FROM flow ORDER BY citation_rows DESC")
    csv("korea_inbound_sources", """SELECT pc.country policy_country,count(*) citation_rows,count(DISTINCT c.policy_document_id) policy_documents FROM citations c JOIN works w USING(oaid_w) JOIN pc USING(policy_document_id) WHERE w.country='KR' GROUP BY 1 ORDER BY 2 DESC""")
    csv("korea_outbound_countries", """SELECT coalesce(research_country,'Unassigned') research_country,citation_rows FROM flow WHERE policy_country='South Korea' ORDER BY citation_rows DESC""")
    csv("direction_domains", """WITH d AS (
        SELECT 'Korean policy → research' direction,wd.domain,count(*) citation_rows FROM citations c JOIN pc USING(policy_document_id) JOIN wd USING(oaid_w) WHERE pc.country='South Korea' GROUP BY 1,2
        UNION ALL SELECT 'Policy → Korean research',wd.domain,count(*) FROM citations c JOIN works w USING(oaid_w) JOIN wd USING(oaid_w) WHERE w.country='KR' GROUP BY 1,2)
        SELECT *,100.0*citation_rows/sum(citation_rows) OVER(PARTITION BY direction) share_pct FROM d""")
    csv("source_types", """SELECT pt.source_type,count(*) citation_rows,count(DISTINCT c.policy_document_id) policy_documents FROM citations c JOIN pt USING(policy_document_id) GROUP BY 1 ORDER BY 2 DESC""")
    csv("source_type_domains", "SELECT pt.source_type,wd.domain,count(*) citation_rows FROM citations JOIN pt USING(policy_document_id) JOIN wd USING(oaid_w) GROUP BY 1,2")
    csv("policy_sources", """SELECT pc.country policy_country,count(*) citation_rows,count(DISTINCT c.policy_document_id) policy_documents,count(*)::DOUBLE/count(DISTINCT c.policy_document_id) citations_per_document FROM citations c JOIN pc USING(policy_document_id) GROUP BY 1 ORDER BY 2 DESC""")
    csv("korea_institutions", """SELECT p.policy_source_id,p.policy_source_title,count(*) citation_rows,count(DISTINCT c.policy_document_id) policy_documents FROM citations c JOIN pc USING(policy_document_id) JOIN policy p USING(policy_document_id) WHERE pc.country='South Korea' GROUP BY 1,2 ORDER BY 3 DESC""")
    csv("publication_year", """SELECT w.pubyear,count(*) citation_rows,count(DISTINCT c.oaid_w) cited_works FROM citations c JOIN works w USING(oaid_w) GROUP BY 1 ORDER BY 1""")
    csv("topic_metrics", """SELECT t.topic_id,t.topic,t.domain,t.field,t.subfield,
        sum(r.n) citation_rows,count(*) cited_works,
        count(*) FILTER(WHERE w.pubyear BETWEEN 2023 AND 2025) recent_works,
        count(*) FILTER(WHERE w.pubyear BETWEEN 1 AND 2025) eligible_year_works,
        sum(r.n)::DOUBLE/count(*) citations_per_work,
        100.0*count(*) FILTER(WHERE w.pubyear BETWEEN 2023 AND 2025)/nullif(count(*) FILTER(WHERE w.pubyear BETWEEN 1 AND 2025),0) recent_share_pct
        FROM topics t JOIN repeat r USING(oaid_w) JOIN works w USING(oaid_w)
        GROUP BY 1,2,3,4,5 ORDER BY citation_rows DESC""")
    csv("country_assignment", "SELECT country_assignment_stage,count(*) cited_works,sum(n) citation_rows FROM repeat JOIN works USING(oaid_w) GROUP BY 1")
    csv("country_ties", "SELECT ror_mode_tied,count(*) cited_works,sum(n) citation_rows FROM repeat JOIN works USING(oaid_w) GROUP BY 1")
    csv("country_coverage_by_policy_source", "SELECT policy_country,sum(citation_rows) total_citations,sum(CASE WHEN research_country IS NOT NULL THEN citation_rows ELSE 0 END) known_citations FROM flow GROUP BY 1 ORDER BY 2 DESC")
    # Explicit sensitivity: unrestricted mapping and ROR-only assignment.
    csv("korea_country_sensitivity", """WITH x AS (
        SELECT 'Unique DOI; waterfall' variant,w.country country FROM citations c JOIN pc USING(policy_document_id) JOIN works w USING(oaid_w) WHERE pc.country='South Korea'
        UNION ALL SELECT 'All DOI matches; waterfall',w.country FROM citations_all c JOIN pc USING(policy_document_id) JOIN works w USING(oaid_w) WHERE pc.country='South Korea'
        UNION ALL SELECT 'Unique DOI; ROR only',w.ror_country FROM citations c JOIN pc USING(policy_document_id) JOIN works w USING(oaid_w) WHERE pc.country='South Korea')
        SELECT variant,count(*) total_citations,count(country) known_citations,
        count(*) FILTER(WHERE country='US') us_citations,count(*) FILTER(WHERE country='KR') kr_citations,
        100.0*count(*) FILTER(WHERE country='US')/nullif(count(country),0) us_share_known_pct,
        100.0*count(*) FILTER(WHERE country='KR')/nullif(count(country),0) kr_share_known_pct FROM x GROUP BY 1""")
    # Technical reference uses cited unique works in this joined sample, not all OA production.
    csv("korea_expected_country_shares", """WITH supply AS (
        SELECT wd.domain,w.country,count(*) n FROM repeat JOIN works w USING(oaid_w) JOIN wd USING(oaid_w) WHERE w.country IS NOT NULL GROUP BY 1,2),
        shares AS (SELECT *,n::DOUBLE/sum(n) OVER(PARTITION BY domain) s FROM supply),
        demand AS (SELECT domain,count(*) n FROM citations JOIN pc USING(policy_document_id) JOIN wd USING(oaid_w) WHERE pc.country='South Korea' GROUP BY 1),
        weights AS (SELECT *,n::DOUBLE/sum(n) OVER() weight FROM demand)
        SELECT country,sum(weight*s)*100 expected_share_pct FROM shares JOIN weights USING(domain) GROUP BY 1 ORDER BY 2 DESC""")
    # Country-domain profiles preserve each direction's population and domain deduplication.
    csv("country_domain", "SELECT pc.country policy_country,wd.domain,count(*) citation_rows FROM citations JOIN pc USING(policy_document_id) JOIN wd USING(oaid_w) GROUP BY 1,2")
    inputs = [MAPPING, RAW/'01__Overton_20261004_raw__MAIN.parquet', RAW/'09__Overton_20261004_raw__SUB__policy_source_country.parquet', RAW/'10__Overton_20261004_raw__SUB__policy_source_type.parquet', RAW/'12__Overton_20261004_raw__SUB__dois_cited.parquet']
    manifest = {"overton_snapshot":"2026-10-04", "openalex_snapshot":"2026-06-25", "analysis_date":"2026-10-08", "doi_rule":"lowercase DOI; remove Unicode format controls and whitespace; input-bound fresh mapping; exclude DOIs mapping to multiple distinct work IDs; distinct document/work pairs", "country_rule":"first author_position=first; ROR ISO2 mode by affiliation row frequency, alphabetical tie break; otherwise exactly one OA institution ISO2; otherwise unresolved", "country_fallback_difference":"2025 baseline used raw_string_country_code; absent in 20260625, replaced by oaid_i_country_code", "domain_rule":"distinct work/domain; multiple domains allowed", "enrichment":complete, "doi_mapping":json.loads((STAGE/'doi_mapping_complete.json').read_text()), "inputs":[], "scripts":{}}
    for p in inputs:
        h = hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
        manifest['inputs'].append({"file":p.name,"bytes":p.stat().st_size,"sha256":h.hexdigest()})
    for name in ['map_online_update_202610.py','extract_online_update_202610.py','analyze_online_update_202610.py']:
        manifest['scripts'][name]=hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest()
    enrichment_hash = hashlib.sha256()
    for p in sorted((STAGE/'enrichment').glob('*.parquet')):
        enrichment_hash.update(p.name.encode())
        enrichment_hash.update(hashlib.sha256(p.read_bytes()).digest())
    manifest['enrichment']['parquet_collection_sha256'] = enrichment_hash.hexdigest()
    manifest['public_aggregate_sha256'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PUBLIC.glob('*.csv'))}
    (PUBLIC/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    con.close()
    from refine_online_update_202610 import main as refine
    refine()
    print(f"Completed {PUBLIC}", flush=True)


if __name__ == '__main__':
    main()
