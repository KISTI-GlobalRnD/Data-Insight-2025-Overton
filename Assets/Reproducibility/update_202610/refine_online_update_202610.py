#!/usr/bin/env python3
"""Refine October aggregates from the read-only joined stage, preserving baseline inputs."""
from pathlib import Path
import hashlib
import json
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT/'local_runs/overton20261004_oa20260625_online'
PUBLIC = ROOT/'Data_Insight/Assets/Reproducibility/update_202610'
BASE = ROOT/'Output/Data_Insight/report_figures'
OUT = 'Korean policy → research'
IN = 'Policy → Korean research'

def main():
    con = duckdb.connect()
    con.execute("SET threads=4; SET memory_limit='12GB'; SET enable_progress_bar=false")
    con.execute(f"SET temp_directory='{STAGE}/refinement_tmp'")
    con.execute(f"ATTACH '{STAGE}/analysis.duckdb' AS latest (READ_ONLY)")
    def csv(name, sql):
        con.execute(f"COPY ({sql}) TO '{PUBLIC}/{name}.csv' (HEADER)")
    assert con.execute('SELECT count(*)-count(DISTINCT policy_document_id) FROM latest.policy').fetchone()[0] == 0
    con.execute('''CREATE TEMP TABLE types AS SELECT policy_document_id,
      bool_or(source_type='think tank') is_think_tank FROM latest.pt GROUP BY 1''')
    con.execute(f'''CREATE TEMP TABLE kc AS
      WITH pairs AS (
        SELECT '{OUT}' direction,c.* FROM latest.citations c WHERE EXISTS
          (SELECT 1 FROM latest.pc WHERE pc.policy_document_id=c.policy_document_id AND country='South Korea')
        UNION ALL SELECT '{IN}',c.* FROM latest.citations c JOIN latest.works w USING(oaid_w) WHERE w.country='KR')
      SELECT pairs.*,w.country,p.policy_source_id,p.policy_source_title,
        try_cast(substr(p.published_on,1,4) AS INTEGER) policy_year,
        CASE WHEN t.is_think_tank THEN 'Think tank' ELSE 'Other sources (including unassigned type)' END source_group,
        t.policy_document_id IS NULL type_unassigned
      FROM pairs JOIN latest.works w USING(oaid_w) JOIN latest.policy p USING(policy_document_id)
      LEFT JOIN types t USING(policy_document_id)''')
    con.execute('''CREATE TEMP TABLE kd AS SELECT kc.*,wd.domain,
      count(*) OVER(PARTITION BY direction,policy_document_id,oaid_w) n_domains
      FROM kc JOIN latest.wd wd USING(oaid_w)''')
    counts = dict(con.execute('SELECT direction,count(*) FROM kc GROUP BY 1').fetchall())
    profile = pd.read_csv(PUBLIC/'data_profile.csv').set_index('indicator').value
    assert counts == {OUT:int(profile['korean_policy_citations']),IN:int(profile['citations_to_korean_research'])}
    print('Direction populations',counts,flush=True)
    # Private row-level audit inputs are never copied into the public bundle.
    con.execute(f"COPY kc TO '{STAGE}/refinement_citations.parquet' (FORMAT PARQUET)")
    con.execute(f"COPY kd TO '{STAGE}/refinement_domains.parquet' (FORMAT PARQUET)")
    csv('korea_institution_domains',f'''WITH d AS (
      SELECT policy_source_id,policy_source_title,domain,count(*) domain_assignments
      FROM kd WHERE direction='{OUT}' GROUP BY 1,2,3)
      SELECT *,100.0*domain_assignments/sum(domain_assignments) OVER(PARTITION BY policy_source_id) share_pct
      FROM d ORDER BY policy_source_id,domain''')
    csv('korea_direction_source_groups', '''WITH c AS (
      SELECT direction,source_group,count(*) citation_pairs,count(DISTINCT policy_document_id) policy_documents,
      count(*) FILTER(WHERE type_unassigned) unassigned_type_pairs FROM kc GROUP BY 1,2),
      d AS (SELECT direction,source_group,count(*) domain_assignments,
        count(*) FILTER(WHERE domain='Social Sciences') social_assignments FROM kd GROUP BY 1,2)
      SELECT c.*,d.domain_assignments,d.social_assignments,
        100.0*d.social_assignments/d.domain_assignments social_share_pct,
        100.0*d.domain_assignments/sum(d.domain_assignments) OVER(PARTITION BY direction) domain_weight_pct
      FROM c JOIN d USING(direction,source_group) ORDER BY direction,source_group''')
    csv('korea_source_group_decomposition',f'''WITH d AS (
      SELECT direction,source_group,count(*) n,count(*) FILTER(WHERE domain='Social Sciences') s
      FROM kd GROUP BY 1,2), x AS (
      SELECT *,n::DOUBLE/sum(n) OVER(PARTITION BY direction) w,s::DOUBLE/n p FROM d),
      a AS (SELECT source_group,w wo,p po FROM x WHERE direction='{OUT}'),
      b AS (SELECT source_group,w wi,p pi FROM x WHERE direction='{IN}')
      SELECT source_group,100*(wo-wi)*(po+pi)/2 composition_pp,
        100*(po-pi)*(wo+wi)/2 within_group_pp FROM a JOIN b USING(source_group)''')
    # Four definitions intentionally retain the established baseline sensitivity contract.
    csv('korea_domain_weighting_sensitivity', '''WITH full_d AS (
      SELECT direction,domain,count(*)::DOUBLE weight FROM kd GROUP BY 1,2),
      unique_d AS (SELECT direction,domain,count(DISTINCT oaid_w)::DOUBLE weight FROM kd GROUP BY 1,2),
      doc_d AS (SELECT direction,policy_document_id,domain,count(*)::DOUBLE n FROM kd GROUP BY 1,2,3),
      doc_w AS (SELECT direction,domain,sum(n/sum_n) weight FROM
        (SELECT *,sum(n) OVER(PARTITION BY direction,policy_document_id) sum_n FROM doc_d) GROUP BY 1,2),
      frac AS (SELECT direction,domain,sum(1.0/n_domains) weight FROM kd GROUP BY 1,2),
      all_w AS (
        SELECT 'citation_rows_full_domain' variant,* FROM full_d UNION ALL
        SELECT 'unique_works_full_domain',* FROM unique_d UNION ALL
        SELECT 'policy_documents_equal_weight',* FROM doc_w UNION ALL
        SELECT 'citation_rows_fractional_domain',* FROM frac)
      SELECT *,sum(weight) OVER(PARTITION BY variant,direction) total_weight,
        100*weight/sum(weight) OVER(PARTITION BY variant,direction) share_pct
      FROM all_w ORDER BY variant,direction,domain''')
    # Country expectation: primary uses exactly the country+domain-known citation population.
    con.execute('''CREATE TEMP TABLE supply AS
      WITH n AS (SELECT wd.domain,w.country,count(*) n FROM latest.repeat
        JOIN latest.works w USING(oaid_w) JOIN latest.wd wd USING(oaid_w)
        WHERE w.country IS NOT NULL GROUP BY 1,2)
      SELECT *,n::DOUBLE/sum(n) OVER(PARTITION BY domain) country_share FROM n''')
    csv('expected_country_domain_reference', 'SELECT domain,country,n cited_unique_works,100*country_share country_share_pct FROM supply ORDER BY domain,country')
    con.execute(f'''CREATE TEMP TABLE demand AS WITH x AS (
      SELECT 'legacy_all_full_domain' variant,domain,1.0 weight FROM kd WHERE direction='{OUT}'
      UNION ALL SELECT 'known_full_domain',domain,1.0 FROM kd WHERE direction='{OUT}' AND country IS NOT NULL
      UNION ALL SELECT 'known_fractional_domain',domain,1.0/n_domains FROM kd WHERE direction='{OUT}' AND country IS NOT NULL)
      SELECT variant,domain,sum(weight) weight FROM x GROUP BY 1,2''')
    csv('korea_expected_country_variants', '''WITH weights AS (
      SELECT *,weight/sum(weight) OVER(PARTITION BY variant) w FROM demand)
      SELECT variant,country,100*sum(w*country_share) expected_share_pct FROM weights JOIN supply USING(domain)
      GROUP BY 1,2 ORDER BY variant,expected_share_pct DESC''')
    csv('korea_expected_domain_weights','''SELECT *,100*weight/sum(weight) OVER(PARTITION BY variant) share_pct
      FROM demand ORDER BY variant,domain''')
    csv('korea_expected_country_shares',f'''WITH weights AS (
      SELECT domain,weight/sum(weight) OVER() w FROM demand WHERE variant='known_fractional_domain')
      SELECT country,100*sum(w*country_share) expected_share_pct FROM weights JOIN supply USING(domain)
      GROUP BY 1 ORDER BY 2 DESC''')
    csv('korea_expected_country_population',f'''SELECT 'known_fractional_domain' variant,
      count(*) eligible_citation_pairs,count(*) FILTER(WHERE country='US') us_citations,
      100.0*count(*) FILTER(WHERE country='US')/count(*) observed_us_share_pct,
      (SELECT count(*) FROM kc WHERE direction='{OUT}' AND country IS NOT NULL) all_country_known_pairs,
      (SELECT count(*) FROM kd WHERE direction='{OUT}' AND country IS NOT NULL) eligible_domain_assignments
      FROM kc WHERE direction='{OUT}' AND country IS NOT NULL
      AND EXISTS(SELECT 1 FROM latest.wd WHERE wd.oaid_w=kc.oaid_w)''')
    baseline = pd.read_csv(BASE/'20251026_korea_policy_source_concentration.csv')
    con.register('baseline_sources',baseline)
    csv('korea_common_institutions',f'''WITH n AS (SELECT policy_source_id,policy_source_title,
      count(*) latest_citations,count(DISTINCT policy_document_id) latest_policy_documents
      FROM kc WHERE direction='{OUT}' GROUP BY 1,2)
      SELECT b.source_slug,b.citations baseline_citations,b.policy_documents baseline_policy_documents,
        n.policy_source_title,n.latest_citations,n.latest_policy_documents,
        n.policy_source_id IS NOT NULL in_both FROM baseline_sources b LEFT JOIN n
        ON b.source_slug=n.policy_source_id ORDER BY b.citations DESC''')
    con.execute('''CREATE TEMP TABLE common_ids AS SELECT source_slug FROM baseline_sources WHERE EXISTS
      (SELECT 1 FROM kc WHERE kc.policy_source_id=baseline_sources.source_slug AND direction='Korean policy → research')''')
    con.execute(f'''CREATE TEMP TABLE scopes AS SELECT 'All latest Korean sources' sample_scope,kc.* FROM kc WHERE direction='{OUT}'
      UNION ALL SELECT 'Institutions present in both editions',kc.* FROM kc WHERE direction='{OUT}' AND policy_source_id IN (SELECT * FROM common_ids)
      UNION ALL SELECT 'Common institutions; policy years 2010–2024',kc.* FROM kc WHERE direction='{OUT}' AND policy_source_id IN (SELECT * FROM common_ids) AND policy_year BETWEEN 2010 AND 2024''')
    csv('korea_common_institution_scopes','''WITH c AS (SELECT sample_scope,count(*) citation_pairs,
      count(DISTINCT policy_document_id) policy_documents,count(DISTINCT policy_source_id) institutions,
      count(country) country_known_pairs,100.0*count(*) FILTER(WHERE country='US')/nullif(count(country),0) us_share_known_pct,
      100.0*count(*) FILTER(WHERE policy_source_id IN ('kdi','kiep'))/count(*) kdi_kiep_citation_share_pct FROM scopes GROUP BY 1),
      d AS (SELECT sample_scope,count(*) domain_assignments,100.0*count(*) FILTER(WHERE domain='Social Sciences')/count(*) social_share_pct
        FROM scopes JOIN latest.wd USING(oaid_w) GROUP BY 1)
      SELECT * FROM c JOIN d USING(sample_scope) ORDER BY citation_pairs DESC''')
    old_weight = pd.read_csv(BASE/'20251026_korea_field_gap_weighting_sensitivity.csv').set_index('weighting')
    old_missing = pd.read_csv(BASE/'20251026_korea_research_country_missingness.csv')
    old_country = pd.read_csv(BASE/'20251026_korea_policy_research_flows_top10.csv')
    old_us = old_country[(old_country.direction.str.startswith('Outbound')) & (old_country.entity=='USA')].iloc[0]
    old_overall = old_missing[old_missing.dimension=='overall'].iloc[0]
    latest_domains = pd.read_csv(PUBLIC/'direction_domains.csv')
    social = latest_domains[latest_domains.domain=='Social Sciences'].set_index('direction').share_pct
    latest_us = pd.read_csv(PUBLIC/'korea_outbound_countries.csv').set_index('research_country').citation_rows
    rows = [
      ('Korean policy citation pairs',old_overall.citations,counts[OUT],'pairs'),
      ('Korean citing policy documents',baseline.policy_documents.sum(),profile['korean_policy_documents'],'documents'),
      ('U.S. share; research country known',100*old_us['share'],100*latest_us['US']/(counts[OUT]-latest_us['Unassigned']),'percent'),
      ('Research country unassigned',100*old_overall.missing_share,100*latest_us['Unassigned']/counts[OUT],'percent'),
      ('Social sciences; Korean policy → research',100*old_weight.loc['citation_rows_full_domain','korea_policy_to_research_social_share'],social[OUT],'percent'),
      ('Social sciences; policy → Korean research',100*old_weight.loc['citation_rows_full_domain','policy_to_korea_research_social_share'],social[IN],'percent'),
      ('KDI/KIEP citation share',100*baseline[baseline.source_slug.isin(['kdi','kiep'])].citations.sum()/baseline.citations.sum(),100*con.execute(f"SELECT count(*) FROM kc WHERE direction='{OUT}' AND policy_source_id IN ('kdi','kiep')").fetchone()[0]/counts[OUT],'percent')]
    pd.DataFrame(rows,columns=['indicator','baseline_2025','latest_202610','unit']).to_csv(PUBLIC/'edition_indicator_comparison.csv',index=False)
    gap = social[OUT]-social[IN]
    decomposition = pd.read_csv(PUBLIC/'korea_source_group_decomposition.csv')
    assert abs(decomposition[['composition_pp','within_group_pp']].to_numpy().sum()-gap)<1e-9
    manifest = json.loads((PUBLIC/'provenance.json').read_text())
    manifest['refinement'] = {
      'expected_country_rule':'Country+domain-known Korean citation pairs; each pair split equally over its distinct assigned domains; reference uses known-country cited unique works within each domain. Observed share uses exactly the same eligible pairs.',
      'source_groups':'Exclusive: any top-level think tank tag versus all remaining documents, explicitly including type-unassigned documents. Symmetric two-group descriptive decomposition of domain-assignment social-science gap; not causal.',
      'common_institutions':'Exact source ID intersection with all nine source IDs in the published baseline institution table; all comparisons restricted within the latest snapshot, not behavioral time trends.',
      'weighting':'Full citation-domain assignments; distinct work-domain assignments; equal document weight among documents with domains; fractional citation-domain weight summing to one per citation.',
      'baseline_inputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'20251026_korea_policy_source_concentration.csv',BASE/'20251026_korea_field_gap_weighting_sensitivity.csv',BASE/'20251026_korea_research_country_missingness.csv',BASE/'20251026_korea_policy_research_flows_top10.csv']}}
    for name in ['refine_online_update_202610.py','analyze_online_update_202610.py']:
        manifest['scripts'][name] = hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest()
    manifest['public_aggregate_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PUBLIC.glob('*.csv'))}
    (PUBLIC/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    con.close()
    print('Refined aggregates and provenance complete',flush=True)

if __name__=='__main__':
    main()
