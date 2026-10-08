#!/usr/bin/env python3
"""Synchronize landing copy, bilingual labels and assets to the online aggregates."""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]


def main():
    data=json.loads((ROOT/'Data_Insight/Assets/Reproducibility/update_202610/headline_metrics.json').read_text())
    m={k:(f'{v:.1f}' if isinstance(v,float) else v) for k,v in data.items()}
    text={
      'hero.kicker':'2026년 10월 온라인 업데이트',
      'hero.lede':f"한국 연구를 인용한 상위 3개 정책 출처의 합계 비중은 {m['top3']}%였다. 한국 정책문헌이 인용한 연구에서는 국가가 확인되는 인용 가운데 미국 연구가 {m['us']}%를 차지했다. 사회과학 비중은 한국 정책문헌이 인용한 연구에서 {m['socialout']}%, 정책문헌에 인용된 한국 연구에서 {m['socialin']}%로, 두 방향의 차이는 {m['socialgap']}%p였다.",
      'hero.cta.report':'최신 온라인 결과 보기',
      'hero.cta.si':'2025 기준 보조자료 보기',
      'hero.stat.sourcing':f"한국 정책문헌이 인용한 미국 연구 비중 · 국가 확인 인용 기준",
      'hero.meta.snapshot':'데이터 스냅샷: Overton 2026-10-04 · OpenAlex 2026-06-25 · 고유 DOI 연결 인용 기준',
      'story.hub_country.body':'전체 인용 규모와 인용이 있는 정책문헌당 평균은 서로 다른 지표다. 그림은 인용 총 건수 상위 10개 정책 출처를 같은 순서로 보여준다.',
      'story.hub_type.body':'정부·싱크탱크·국제기구 등 최상위 출처 유형별로 인용 연구의 도메인 구성을 비교한다. 같은 논문의 같은 도메인은 한 번만 세고, 유형 안에서 비중을 계산했다.',
      'story.korea.body':f"한국 정책문헌이 인용한 연구의 사회과학 비중은 {m['socialout']}%, 정책문헌에 인용된 한국 연구에서는 {m['socialin']}%였다. 국가와 분야 구성을 인용 방향별로 구분해 읽어야 한다.",
      'story.two_speed.body':'인용 건수 상위 300개 토픽에서 최근 논문 비중과 논문당 인용 건수를 비교한다. 최근 비중은 2025년 이하 발행연도 확인 논문 가운데 2023–2025년 발행 논문의 비중이다.',
      'monitor.card1.value':f"사회과학 비중 차이 {m['socialgap']}%p",
      'monitor.card1.body':f"한국 정책문헌이 인용한 연구 {m['socialout']}%와 정책문헌에 인용된 한국 연구 {m['socialin']}%의 차이다.",
      'monitor.card2.value':f"상위 3개 정책 출처 합계 비중 {m['top3']}%",
      'monitor.card2.body':f"{m['source_names']}의 합계다. 정책 출처별 인용 집계 합계를 기준으로 계산했다.",
      'monitor.card3.value':f"관측 {m['expected_observed']}% · 기대 {m['expected']}%",
      'monitor.card3.body':'국가·분야가 모두 확인되는 한국 정책문헌 인용의 미국 연구 비중이다. 인용별 분야 가중치 합을 1로 맞춘 기술적 기대값이며, OpenAlex 전체 연구 생산량을 뜻하지 않는다.',
      'monitor.card4.value':f"KDI·KIEP 합계 {m['institutional']}%",
      'monitor.card4.body':'한국 정책문헌에서 관측된 연구 인용 중 두 기관의 문헌에서 나온 인용의 합계 비중이다. 기관별 수집 범위에 유의해야 한다.',
      'monitor.cta.next':'최신 집계표와 해석 범위 보기',
      'monitor.cta.report':'2025 기준 보고서 PDF 보기',
      'explore.card.report.meta':'2025 기준판 · 편집 전 원고',
      'explore.card.report.title':'2025 기준 보고서 PDF',
      'explore.card.report.desc':'기존 데이터의 분석·그림을 담은 편집 전 원고',
      'explore.card.si.meta':'2025 기준판 · 제68호 교정 반영',
      'explore.card.si.title':'2025 기준 보조자료',
      'explore.card.si.desc':'확정한 장 제목과 설명·용어 교정을 반영한 웹 자료',
      'explore.card.update.meta':'Overton 2026-10-04 · OpenAlex 2026-06-25',
      'explore.card.update.desc':'새로 계산한 결과·그림·집계표와 연결 품질 점검',
      'explore.card.interactive.desc':'2025 기준판의 국가·출처 유형·토픽별 인터랙티브 그림',
      'fig.hub_country.alt':'2026년 10월 분석: 정책 출처별 인용 총 건수와 인용이 있는 정책문헌당 평균',
      'fig.hub_type.alt':'2026년 10월 분석: 최상위 정책 출처 유형별 도메인 구성',
      'fig.korea.alt':'2026년 10월 분석: 한국 연구를 인용한 정책 출처와 한국 정책문헌이 인용한 연구 국가',
      'fig.two_speed.alt':'2026년 10월 분석: 상위 300개 토픽의 논문당 인용 건수와 2023–2025년 발행 논문 비중',
    }
    page=ROOT/'Data_Insight/index.html'
    html=page.read_text()
    for key,value in text.items():
        pattern=r'(<(?P<tag>[\w-]+)\b[^>]*\bdata-i18n="'+re.escape(key)+r'"[^>]*>).*?(</(?P=tag)>)'
        html,n=re.subn(pattern,lambda x:x.group(1)+value+x.group(3),html,flags=re.S)
        # Alt translations are attributes rather than inner text.
        if key.startswith('fig.'):
            alt=r'(<img\b[^>]*alt=")[^"]*("[^>]*data-i18n-attr="alt:'+re.escape(key)+r'")'
            html=re.sub(alt,lambda x:x.group(1)+value+x.group(2),html)
        elif n!=1: raise RuntimeError(f'Missing/duplicate landing copy {key}: {n}')
    html=re.sub(r'(<p\b[^>]*data-i18n-html="hero.lede2"[^>]*>).*?(</p>)',
                lambda x:x.group(1)+'이 페이지는 DOI로 한 논문에 연결되는 정책문헌→학술논문 인용을 분석한 <strong>2026년 10월 온라인 결과</strong>다. 모든 정책문헌·참고문헌을 포괄하지 않는다. 연결된 PDF와 기존 보조자료는 <strong>2025 기준판</strong>이다.'+x.group(2),html,flags=re.S)
    values=iter([m['top3']+'%',m['us']+'%',m['socialgap']+'%p'])
    html=re.sub(r'(<div class="promo-stat__value">).*?(</div>)',lambda x:x.group(1)+next(values)+x.group(2),html)
    html=html.replace('href="./Report/Report_final.pdf" data-i18n="hero.cta.report"','href="./SI/update_202603.html" data-i18n="hero.cta.report" data-i18n-attr="href:hero.cta.report.href"')
    html=html.replace('href="./SI/index.html#report-extended-map" data-i18n="monitor.cta.next"','href="./SI/update_202603.html" data-i18n="monitor.cta.next"')
    for old,new in [('country_citations_top10','policy_sources'),('source_type_domain','source_type_domains'),('korea_flows','korea_flows'),('topic_intensity_vs_recency','topic_intensity_recency')]:
        html=html.replace(f'Assets/Landing/{old}.png',f'Assets/Figures/update_202610/{new}.png')
    page.write_text(html)
    en={
      'hero.kicker':'October 2026 Online Update',
      'hero.lede':f"The top three policy sources account for {m['top3']}% of source-tagged citations to Korean research. Among assigned-country citations from Korean policy documents, U.S. research accounts for {m['us']}%. Social sciences account for {m['socialout']}% of research cited by Korean policy documents and {m['socialin']}% of Korean research cited by policy documents, a gap of {m['socialgap']} percentage points.",
      'hero.lede2':'This page summarizes the <strong>October 2026 online analysis</strong> of DOIs mapping to a single OpenAlex work. It does not cover every policy document or every reference. The linked PDF and other SI pages describe the <strong>2025 baseline edition</strong>.',
      'hero.cta.report':'Read Latest Online Results',
      'hero.cta.report.href':'./SI/update_202603_en.html',
      'hero.cta.si':'Read 2025 Baseline Summary',
      'hero.stat.sourcing':'U.S. research share among assigned-country citations from Korean policy documents',
      'hero.meta.snapshot':'Snapshots: Overton 2026-10-04 · OpenAlex 2026-06-25 · Unique DOI-linked citations',
      'story.hub_country.body':'Citation totals and average citations per citing policy document measure different quantities. Both panels show the same ten sources ranked by total citations.',
      'story.hub_type.body':'Domain composition is calculated within top-level source types. Each work/domain pair is counted once, allowing different domains on the same work.',
      'story.korea.body':f"Social sciences account for {m['socialout']}% of research cited by Korean policy documents and {m['socialin']}% of Korean research cited in policy documents. Read country and domain composition separately for each direction.",
      'story.two_speed.body':'The top 300 topics are compared using citations per cited work and the share published in 2023–2025 among works with a known year up to 2025.',
      'fig.hub_country.alt':'October 2026: policy-source citation totals and averages per citing document',
      'fig.hub_type.alt':'October 2026: domain shares within top-level policy source types',
      'fig.korea.alt':'October 2026: policy sources citing Korean research and countries cited by Korean policy documents',
      'fig.two_speed.alt':'October 2026: citations per cited work and 2023–2025 work shares for the top 300 topics',
      'monitor.card1.value':f"Social-science share gap: {m['socialgap']} pp",
      'monitor.card1.body':f"The difference between {m['socialout']}% in the Korean-policy direction and {m['socialin']}% in the Korean-research direction.",
      'monitor.card2.value':f"Top three policy sources: {m['top3']}%",
      'monitor.card2.body':'Combined share of the three largest categories among source-tagged citations to Korean research.',
      'monitor.card3.value':f"Observed {m['expected_observed']}% · expected {m['expected']}%",
      'monitor.card3.body':'U.S. shares use Korean-policy citations with both country and domain assigned. Each citation has unit domain weight. The expected share is a descriptive reference, not total OpenAlex research production.',
      'monitor.card4.value':f"KDI + KIEP: {m['institutional']}%",
      'monitor.card4.body':'Combined share of citations from Korean policy documents observed in these two institutions. Collection coverage differs across institutions.',
      'monitor.cta.next':'Open Latest Aggregates and Scope',
      'monitor.cta.next.href':'./SI/update_202603_en.html',
      'monitor.cta.report':'Open 2025 Baseline PDF',
      'explore.card.report.meta':'2025 baseline · Korean',
      'explore.card.report.title':'2025 Korean Report PDF',
      'explore.card.report.desc':'The 2025 analysis and figures in the manuscript before publication editing',
      'explore.card.si.meta':'2025 baseline · issue 68 corrections',
      'explore.card.si.title':'2025 Baseline Summary',
      'explore.card.si.desc':'Web explanations with approved editorial corrections and a chapter-title map',
      'explore.card.update.meta':'Overton 2026-10-04 · OpenAlex 2026-06-25',
      'explore.card.update.desc':'Recomputed results, figures, aggregates and linkage checks',
      'explore.card.interactive.desc':'Interactive country, source-type and topic figures for the 2025 baseline',
    }
    jsfile=ROOT/'Data_Insight/Assets/Site/promo.js'
    js=jsfile.read_text()
    for key,value in en.items():
        pattern=r'("'+re.escape(key)+r'"\s*:\s*)"(?:[^"\\]|\\.)*"'
        js,n=re.subn(pattern,lambda x:x.group(1)+json.dumps(value,ensure_ascii=False),js)
        if not n:
            assert key=='hero.cta.report.href'
            js=js.replace('const en = {','const en = {\n    "hero.cta.report.href": "./SI/update_202603_en.html",')
    jsfile.write_text(js)
    print('Landing copy, English translations and four figure paths updated')


if __name__=='__main__':
    main()
