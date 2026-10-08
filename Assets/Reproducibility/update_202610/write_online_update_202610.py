#!/usr/bin/env python3
"""Write the Korean/English update from public aggregates, never literal results."""
from pathlib import Path
import json
import re
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'Data_Insight/Assets/Reproducibility/update_202610'
LINK='../Assets/Reproducibility/update_202610'
FIG='../Assets/Figures/update_202610'
OUT='Korean policy → research'
IN='Policy → Korean research'
INSTITUTION_KO={
    'kihasakr':'한국보건사회연구원 (KIHASA)', 'stepikr':'과학기술정책연구원 (STEPI)',
    'kicjkr':'한국형사·법무정책연구원 (KICJ)', 'kipakr':'한국행정연구원 (KIPA)',
    'kietkr':'산업연구원 (KIET)', 'keikr':'한국환경연구원 (KEI)',
    'krihskr':'국토연구원 (KRIHS)', 'kinukr':'통일연구원 (KINU)',
    'kdi':'한국개발연구원 (KDI)', 'klikr':'한국노동연구원 (KLI)',
    'kiep':'대외경제정책연구원 (KIEP)'}
WEIGHT_KO={
    'citation_rows_full_domain':'인용 기준 (기본)',
    'unique_works_full_domain':'고유 논문 기준',
    'policy_documents_equal_weight':'문헌 동일 가중',
    'citation_rows_fractional_domain':'인용별 도메인 분할'}
WEIGHT_EN={
    'citation_rows_full_domain':'Citation-domain (primary)',
    'unique_works_full_domain':'Unique work-domain',
    'policy_documents_equal_weight':'Equal policy-document weight',
    'citation_rows_fractional_domain':'Fractional citation-domain'}


def number_captions(text,lang):
    count=iter(range(1,7))
    prefix='Figure' if lang=='en' else '그림'
    text=re.sub(r'!\[',lambda m:f'![{prefix} {next(count)}. ',text)
    assert len(re.findall(r'!\[',text))==6
    return text


def read(name):
    return pd.read_csv(DATA/f'{name}.csv',keep_default_na=False)


def table(df, columns):
    lines=['| '+' | '.join(columns.values())+' |','| '+' | '.join(['---']*len(columns))+' |']
    for _,row in df.iterrows():
        values=[]
        for key in columns:
            value=row[key]
            if isinstance(value,float): value=f'{value:,.1f}'
            elif isinstance(value,int): value=f'{value:,}'
            values.append(str(value).replace('|','/'))
        lines.append('| '+' | '.join(values)+' |')
    return '\n'.join(lines)


def embed(name,title,lang='ko'):
    open_label='Open in new window' if lang=='en' else '새 창으로 열기'
    load_label='Load plot' if lang=='en' else '플롯 불러오기'
    number=['korea_flows','korea_domains','policy_sources','source_type_domains','topic_intensity_recency','research_publication_year'].index(name)+1
    title=f"{'Figure' if lang=='en' else '그림'} {number}. {title}"
    return f'''```{{=html}}
<div class="si-plot" data-src="../Assets/Interactive/update_202610/{name}.html" data-height="620" data-title="{title}">
  <div class="si-plot__actions">
    <a class="si-plot__link" href="../Assets/Interactive/update_202610/{name}.html" target="_blank" rel="noopener">{open_label}</a>
    <button type="button" class="si-plot__btn">{load_label}</button>
  </div>
</div>
```'''


def main():
    p=read('data_profile').set_index('indicator').value.to_dict()
    quality=read('doi_linkage_audit').iloc[0]
    inbound=read('korea_inbound_sources')
    top3=inbound.head(3).citation_rows.sum()/inbound.citation_rows.sum()*100
    source_names='·'.join(inbound.head(3).policy_country.replace({'USA':'미국','UK':'영국','IGO':'국제기구','South Korea':'한국'}))
    outbound=read('korea_outbound_countries').set_index('research_country').citation_rows
    total=int(outbound.sum()); unknown=int(outbound.get('Unassigned',0));known=total-unknown
    us=outbound.get('US',0)/known*100;kr=outbound.get('KR',0)/known*100
    missing=unknown/total*100
    repeat=p['works_cited_at_least_twice']/p['cited_works']*100
    domains=read('direction_domains')
    d=domains.pivot(index='domain',columns='direction',values='share_pct')
    socialout=d.loc['Social Sciences','Korean policy → research']
    socialin=d.loc['Social Sciences','Policy → Korean research']
    healthout=d.loc['Health Sciences','Korean policy → research']
    healthin=d.loc['Health Sciences','Policy → Korean research']
    expected=read('korea_expected_country_shares').set_index('country').expected_share_pct['US']
    eligible=read('korea_expected_country_population').iloc[0]
    expected_observed=eligible.observed_us_share_pct
    expected_variants=read('korea_expected_country_variants')
    expected_variants=expected_variants[expected_variants.country=='US'].copy()
    expected_variants=expected_variants.set_index('variant').loc[
        ['legacy_all_full_domain','known_full_domain','known_fractional_domain']].reset_index()
    expected_variants['variant']=expected_variants.variant.replace({
        'legacy_all_full_domain':'이전 계산: 국가 미부여 포함 · 도메인별 각각 집계',
        'known_full_domain':'국가·분야 확인 · 도메인별 각각 집계',
        'known_fractional_domain':'국가·분야 확인 · 인용별 분할 가중 (채택)'})
    institutions=read('korea_institutions')
    kdi_mask=institutions.policy_source_title.str.contains('Korea Development Institute|Korea Institute for International Economic Policy|한국개발연구원|대외경제정책연구원',case=False,regex=True)
    kdi=institutions[kdi_mask]
    assert len(kdi)==2, f'Confirm KDI/KIEP identities before writing: {kdi.to_dict("records")}'
    institution_display=pd.concat([institutions.head(10),kdi]).drop_duplicates('policy_source_id').sort_values('citation_rows',ascending=False)
    institution_social=read('korea_institution_domains')
    institution_social=institution_social[institution_social.domain=='Social Sciences'][['policy_source_id','share_pct']]
    institution_display=institution_display.merge(institution_social,on='policy_source_id',how='left')
    assert institution_display.share_pct.notna().all()
    institution_display_en=institution_display.copy()
    institution_display['policy_source_title']=institution_display.policy_source_id.map(INSTITUTION_KO).fillna(institution_display.policy_source_title)
    institutional=kdi.citation_rows.sum()/total*100
    weighting=read('korea_domain_weighting_sensitivity')
    weighting=weighting[weighting.domain=='Social Sciences'].pivot(index='variant',columns='direction',values='share_pct').reindex(WEIGHT_KO)
    weighting['gap']=weighting[OUT]-weighting[IN]
    weighting=weighting.rename(columns={OUT:'out',IN:'in'}).reset_index()
    weighting_en=weighting.copy()
    weighting_en['variant']=weighting_en.variant.replace(WEIGHT_EN)
    weighting['variant']=weighting.variant.replace(WEIGHT_KO)
    source_groups=read('korea_direction_source_groups')
    groups_en=source_groups.copy()
    groups_en['source_group']=groups_en.source_group.replace({'Other sources (including unassigned type)':'Other sources'})
    groups_ko=source_groups.copy()
    groups_ko['direction']=groups_ko.direction.replace({OUT:'한국 정책문헌 → 연구',IN:'정책문헌 → 한국 연구'})
    groups_ko['source_group']=groups_ko.source_group.replace({'Think tank':'싱크탱크','Other sources (including unassigned type)':'그 외 출처'})
    decomposition=read('korea_source_group_decomposition')
    composition_pp=decomposition.composition_pp.sum()
    within_pp=decomposition.within_group_pp.sum()
    scopes=read('korea_common_institution_scopes')
    common=scopes[scopes.sample_scope=='Institutions present in both editions'].iloc[0]
    scopes_ko=scopes.copy()
    scopes_ko['sample_scope']=scopes_ko.sample_scope.replace({
        'All latest Korean sources':'최신판 전체',
        'Institutions present in both editions':'공통 기관',
        'Common institutions; policy years 2010–2024':'공통 기관 · 2010–2024년 문헌'})
    comparison=read('edition_indicator_comparison')
    comparison_ko=comparison.copy()
    comparison_ko['indicator']=comparison_ko.indicator.replace({
        'Korean policy citation pairs':'한국 정책문헌의 연구 인용 (건)',
        'Korean citing policy documents':'연구 인용이 있는 한국 정책문헌 (편)',
        'U.S. share; research country known':'미국 연구 비중 · 국가 확인 인용 (%)',
        'Research country unassigned':'연구 국가 미부여 (%)',
        'Social sciences; Korean policy → research':'사회과학 · 한국 정책문헌 → 연구 (%)',
        'Social sciences; policy → Korean research':'사회과학 · 정책문헌 → 한국 연구 (%)',
        'KDI/KIEP citation share':'한국 정책문헌 인용 중 KDI·KIEP (%)'})
    for frame in (comparison,comparison_ko):
        for col in ('baseline_2025','latest_202610'):
            frame[col]=[f'{v:,.0f}' if u in ('pairs','documents') else f'{v:.1f}' for v,u in zip(frame[col],frame.unit)]
    qmatch=quality.matched_dois/quality.unique_dois*100
    sensitivity=read('korea_country_sensitivity')
    sensitivity_ko=sensitivity.copy()
    sensitivity_ko['variant']=sensitivity_ko.variant.replace({'Unique DOI; waterfall':'기본 분석 · 국가 순차 부여',
        'All DOI matches; waterfall':'다중 연결 DOI 포함 · 국가 순차 부여','Unique DOI; ROR only':'기본 분석 · ROR 국가만 사용'})
    assignment=read('country_assignment')
    ties=read('country_ties')
    mapped_rows=inbound.citation_rows.sum()
    duplicate_country=mapped_rows-p['citations_to_korean_research']
    # Direction shares are assignment shares when policy sources have multiple roots.
    domain_table=d.rename(columns={'Korean policy → research':'out','Policy → Korean research':'in'}).reset_index()
    ko=f'''---
title: "2026년 10월 데이터 업데이트"
description: "Overton 2026-10-04와 OpenAlex 2026-06-25로 한국의 두 가지 정책-연구 인용 방향과 전체 자료의 주요 지표를 다시 계산했다."
---

**바로가기:** [확장 자료](index.qmd) · [2025 기준 보고서 원고](../Report/Report_final.pdf) · [English summary](update_202603_en.qmd)

**웹 갱신일:** 2026년 10월 8일 · **Overton:** 2026-10-04 · **OpenAlex:** 2026-06-25

::: {{.callout-note}}
## 이번에 갱신한 범위

이 페이지와 메인 첫 화면은 새 데이터로 다시 계산한 온라인 결과다. 연결된 PDF와 기존 방법론·부록·인터랙티브는 2025 기준판이다. 아래의 새 그림과 집계표는 해당 기준판과 구분해 제공한다.

분석 모집단은 Overton에서 DOI로 연결되고 OpenAlex의 한 논문에 대응하는 정책문헌→학술논문 인용이다. 모든 정책문헌이나 모든 참고문헌을 포괄하지 않는다.
:::

## 한국의 두 인용 방향은 새 자료에서도 다르게 구성된다

한국 연구를 인용한 정책 출처에서는 {source_names}의 합계 비중이 **{top3:.1f}%**였다. 한국 정책문헌이 인용한 연구에서는 국가가 확인되는 인용 가운데 미국 연구가 **{us:.1f}%**, 한국 연구가 **{kr:.1f}%**였다. 두 비중은 각각 정책 출처와 연구 국가의 구성을 나타내므로 같은 모집단의 값처럼 비교하지 않는다.

한국 정책문헌이 인용한 연구의 사회과학 비중은 **{socialout:.1f}%**, 정책문헌에 인용된 한국 연구에서는 **{socialin:.1f}%**였다. 보건과학 비중은 각각 **{healthout:.1f}%**, **{healthin:.1f}%**였다. 국가와 분야 구성을 인용 방향별로 구분해서 읽어야 한다는 보고서의 관찰은 이번 결합 자료에서도 확인된다.

## 1. 분석에 포함된 자료

| 항목 | 이번 온라인 분석 |
|---|---:|
| Overton 원자료의 정책문헌 | {int(quality.raw_policy_documents):,}편 |
| DOI가 관측된 고유 정책문헌–DOI 관계 | {int(quality.unique_document_doi_pairs):,}건 |
| 고유 DOI | {int(quality.unique_dois):,}개 |
| OpenAlex와 연결된 DOI | {int(quality.matched_dois):,}개 · {qmatch:.1f}% |
| 한 논문에 대응하는 DOI | {int(quality.unambiguous_dois):,}개 |
| 기본 분석의 정책문헌–논문 인용 | {p['document_work_pairs']:,}건 |
| 기본 분석에서 연구를 인용한 정책문헌 | {p['citing_policy_documents']:,}편 |
| 기본 분석에서 인용된 고유 논문 | {p['cited_works']:,}편 |

같은 정책문헌이 같은 논문을 여러 번 인용해도 한 관계로 센다. DOI는 공백·보이지 않는 서식 문자·대소문자를 정리해 연결하고, 여러 논문에 대응하는 DOI는 기본 분석에서 제외했다. DOI 연결률은 고유 DOI가 기준이며, 기본 분석의 인용 건수는 중복을 제거한 정책문헌–논문 관계가 기준이다. 여기서 논문은 DOI로 연결된 OpenAlex 연구 레코드를 뜻하며, 학술지 논문만으로 문헌 유형을 제한하지 않았다.

## 2. 한국 연구를 인용한 정책 출처와 한국 정책문헌이 인용한 연구 국가

한국 연구가 인용된 관계는 {p['citations_to_korean_research']:,}건이고, 한국 정책문헌이 연구를 인용한 관계는 {total:,}건이었다. 한국 정책문헌 표본에는 연구 인용이 있는 문헌 {p['korean_policy_documents']:,}편이 포함됐다.

![정책 출처별 한국 연구 인용 비중과 한국 정책문헌이 인용한 연구 국가 비중. 왼쪽은 최상위 정책 출처별 인용 집계의 합계를 기준으로, 오른쪽은 연구 국가가 확인되는 인용을 기준으로 계산했다. 양쪽 모두 상위 10개만 표시했다.]({FIG}/korea_flows.png)

그림 양쪽의 국가는 같은 영문 국가명으로 표시했으며, 국제기구와 유럽연합은 별도의 정책 출처 범주다. 오른쪽의 국가 비중 계산에는 전체 {total:,}건 중 국가가 확인되는 {known:,}건을 사용했다. 국가를 부여하지 못한 인용은 {unknown:,}건으로 **{missing:.1f}%**였다. 이 인용을 모두 미국 이외 또는 미국 연구로 배치하면 미국 연구 비중의 기계적 경계는 {outbound.get('US',0)/total*100:.1f}–{(outbound.get('US',0)+unknown)/total*100:.1f}%다. 이 범위는 통계적 신뢰구간이 아니다.

한국 연구의 정책 출처별 집계 합계는 {int(mapped_rows):,}건이다. 정책 출처의 최상위 태그는 상호 배타적이지 않을 수 있어, 고유 인용 관계의 수와 구분한다. 이번 자료에서 두 수의 차이는 {int(duplicate_country):,}건이다. 출처 미부여와 복수 태그가 함께 있으면 차이만으로 복수 태그의 양을 확정할 수 없다.

### 관측 비중과 기대 비중의 비교 대상 맞추기

기대 비중을 계산할 때는 **연구 국가와 도메인이 모두 확인되는 한국 정책문헌의 인용 {int(eligible.eligible_citation_pairs):,}건**으로 비교 대상을 맞췄다. 국가가 확인되는 인용 가운데 분야 정보가 없는 {int(eligible.all_country_known_pairs-eligible.eligible_citation_pairs):,}건은 이 비교에서 제외했다. 도메인이 여러 개 붙은 논문은 인용 1건의 가중치를 도메인 수로 나누어, 인용마다 가중치 합이 1이 되게 했다.

이 분야 가중치와 **결합 표본에서 인용된 고유 논문의 분야별 1저자 국가 구성**을 결합한 미국 연구의 기대 비중은 **{expected:.1f}%**, 같은 인용 모집단의 관측 비중은 **{expected_observed:.1f}%**로, 차이는 **{expected_observed-expected:.1f}%p**였다. 이는 정책문헌에 인용된 표본 안에서 만든 기술적 비교 기준이며, OpenAlex 전체 연구 생산량이나 바람직한 인용 비중이 아니다. 그림 1의 국가 비중은 분야 정보의 유무와 관계없이 국가 확인 인용 전체를 사용한다.

{table(expected_variants,{'variant':'기대 비중 계산 조건','expected_share_pct':'미국 기대 비중 %'})}

이전 계산은 국가 미부여 인용까지 포함한 분야 구성을 사용했다. 중간 계산은 국가·분야 확인 인용으로 대상을 좁혔지만 도메인이 많은 인용에 더 큰 가중치를 부여한다. 마지막 행을 인용 단위의 관측 비중과 비교하는 기준으로 채택했다. 세 계산의 [분야 가중치]({LINK}/korea_expected_domain_weights.csv)와 [분야별 국가 구성]({LINK}/expected_country_domain_reference.csv)을 함께 제공한다.

{embed('korea_flows','한국의 두 인용 방향: 정책 출처와 연구 국가')}

## 3. 두 방향의 분야 구성

{table(domain_table,{'domain':'도메인','out':'한국 정책문헌이 인용한 연구 %','in':'정책문헌에 인용된 한국 연구 %'})}

![한국의 두 가지 인용 방향별 도메인 구성. 같은 논문의 같은 도메인은 한 번만 세며, 서로 다른 도메인이 부여되면 각각 포함한다. 각 방향의 도메인 부여 건수 합계를 100%로 정규화했다.]({FIG}/korea_domains.png)

사회과학 비중 차이는 {socialout-socialin:.1f}%p였다. 도메인은 OpenAlex가 논문에 부여한 토픽에서 가져왔다. 같은 논문에 여러 도메인이 있을 수 있으므로, 이 비중은 논문을 하나의 분야에만 배정한 비중과 다르다. 전체 기본 분석에서 도메인을 부여하지 못한 인용은 {p['citations_without_domain']:,}건이다.

{embed('korea_domains','한국의 두 인용 방향: 분야 구성')}

### 가중 방식에 따른 민감도

{table(weighting,{'variant':'가중 방식','out':'한국 정책문헌 → 연구 %','in':'정책문헌 → 한국 연구 %','gap':'사회과학 비중 차이 %p'})}

표의 두 비중은 모두 사회과학을 나타낸다. 기본 분석은 인용마다 부여된 도메인을 각각 센다. 고유 논문 방식은 여러 문헌에 인용된 논문도 방향별로 한 번만 세고, 문헌 동일 가중 방식은 분야 정보가 있는 문헌마다 사회과학 도메인 비중을 계산한 뒤 평균한다. 분할 가중 방식은 인용마다 가중치 합을 1로 맞춘다. 분야가 없는 인용은 각 방식의 분야 구성 계산에서 제외한다.

사회과학 비중 차이는 네 방식에서 **{weighting.gap.min():.1f}–{weighting.gap.max():.1f}%p**였다. 차이의 크기는 가중 방식에 따라 달라졌지만, 한국 정책문헌이 인용한 연구에서 사회과학 비중이 더 높다는 방향은 유지됐다. 이 범위는 계산 방식에 따른 결과의 범위이며 신뢰구간이 아니다.

## 4. 한국 정책문헌 표본의 기관 구성

KDI·KIEP 문헌에서 관측된 인용은 {int(kdi.citation_rows.sum()):,}건으로, 한국 정책문헌의 연구 인용 중 **{institutional:.1f}%**였다. 연구 인용이 있는 두 기관 문헌은 {int(kdi.policy_documents.sum()):,}편이다. 아래 표에는 인용 건수 상위 10곳과 KDI·KIEP를 제시했다. 나머지 기관은 [전체 집계표]({LINK}/korea_institutions.csv)에서 확인한다.

{table(institution_display,{'policy_source_title':'정책 출처 기관','citation_rows':'인용 건수','policy_documents':'인용 문헌 수','share_pct':'사회과학 %'})}

기관별 사회과학 비중은 해당 기관의 도메인 부여 건수를 기준으로 계산했다. 표시한 한국어 기관명과 약칭은 독자의 이해를 위한 표기이며, 집계표의 원래 기관명·식별자는 유지했다. 기관별 관측 범위가 다르면 표본의 구성도 달라질 수 있다. 이 수치만으로 국내 정책기관 전체의 연구 활용 성향이나 개별 기관의 정책 영향력을 판단할 수 없다. 해외 유사 싱크탱크와의 비교는 기존 2025 기준판의 분석이다.

### 출처 유형 구성과 유형 안의 분야 구성

최상위 유형에 싱크탱크가 하나라도 부여된 문헌과 그 외 문헌으로 나눴다. 두 집단은 서로 겹치지 않으며, 유형 미부여 문헌은 그 외 출처에 포함한다. 이번 두 방향의 분석에 포함된 인용 중 유형 미부여는 {int(source_groups.unassigned_type_pairs.sum()):,}건이었다. 아래의 출처 비중과 사회과학 비중은 모두 **도메인 부여 건수**를 기준으로 한다.

{table(groups_ko,{'direction':'인용 방향','source_group':'출처 집단','domain_weight_pct':'출처 비중 %','social_share_pct':'집단 내 사회과학 %'})}

두 방향의 사회과학 비중 차이 {socialout-socialin:.1f}%p를 대칭 분해하면, 출처 집단의 구성비 차이에 해당하는 항이 **{composition_pp:.1f}%p**, 각 집단 안의 사회과학 비중 차이에 해당하는 항이 **{within_pp:.1f}%p**였다. 싱크탱크의 비중 차이와 각 집단 안의 분야 구성 차이가 함께 관측된다. 이는 두 집단으로 나눈 기술적 분해이며 정책 수요의 원인이나 기관의 효과를 추정한 결과가 아니다.

분해식은 구성 항 `Σ(출처 비중 차이 × 집단 내 사회과학 비중의 양방향 평균)`과 집단 내 항 `Σ(집단 내 사회과학 비중 차이 × 출처 비중의 양방향 평균)`의 합이다. 집단별 항은 [분해 집계표]({LINK}/korea_source_group_decomposition.csv)에서 확인한다.

## 5. 전체 자료의 정책 출처·시간·반복 인용

### 정책 출처별 총량과 문헌당 평균

![인용 총 건수 상위 10개 정책 출처의 인용 총량과 인용이 있는 정책문헌당 평균. 두 패널은 같은 출처를 같은 순서로 표시한다. 평균은 기본 분석에 포함된 인용이 한 건 이상인 문헌을 기준으로 계산했다.]({FIG}/policy_sources.png)

출처의 전체 인용 규모와 인용이 있는 정책문헌당 평균 학술논문 인용 건수는 구분해야 한다. 오른쪽은 왼쪽의 상위 10개 출처에 대한 평균이며, 평균 자체의 전체 순위가 아니다. [정책 출처 집계표]({LINK}/policy_sources.csv)에서 다른 출처도 확인할 수 있다.

{embed('policy_sources','정책 출처별 인용 총량과 문헌당 평균')}

![최상위 정책 출처 유형별 인용 연구의 도메인 구성. 최상위 유형 안에서 도메인 부여 건수의 합계를 100%로 정규화했다.]({FIG}/source_type_domains.png)

{embed('source_type_domains','정책 출처 유형별 인용 연구의 분야 구성')}

### 토픽별 최근 논문 비중과 논문당 인용 건수

![DOI 연결 인용 건수 상위 300개 토픽의 인용된 논문당 인용 건수와 최근 고유 논문 비중.]({FIG}/topic_intensity_recency.png)

최근 고유 논문 비중은 발행연도가 확인되는 **2025년 이하**의 고유 논문 가운데 **2023–2025년** 발행 논문의 비중이다. 2026년은 완결된 발행연도가 아니어서 제외했다. 2025 기준판의 2022–2024년 창과 다르므로 두 값을 그대로 성장률처럼 비교하지 않는다. 토픽의 최근 논문 비중과 논문당 인용 건수는 중요도나 정책 효과를 측정하지 않는다.

{embed('topic_intensity_recency','토픽별 논문당 인용 건수와 2023–2025년 발행 논문 비중')}

### 발행연도와 반복 인용

![인용된 연구의 발행연도별 DOI 연결 인용 건수. 1990–2026년만 표시했으며, 회색 구간의 2026년은 완결되지 않은 연도다. 정책문헌의 발행연도별 추이가 아니다.]({FIG}/research_publication_year.png)

{embed('research_publication_year','인용된 연구의 발행연도별 인용 건수')}

두 개 이상의 서로 다른 정책문헌에 인용된 고유 논문은 {p['works_cited_at_least_twice']:,}편으로, 인용된 고유 논문의 **{repeat:.1f}%**였다. 같은 문헌 안의 반복 언급을 세는 지표가 아니며, 독립된 정책 채택이나 인과적 영향의 증거도 아니다. 서로 다른 문헌 ID 사이에 유사·중복 문헌이 포함될 가능성은 남아 있다.

## 6. 연결 품질과 해석 범위

### DOI가 여러 논문에 연결되는 경우

고유 DOI {int(quality.ambiguous_dois):,}개가 여러 OpenAlex 논문에 연결됐다. 해당 DOI가 등장한 정책문헌–DOI 관계는 {int(quality.ambiguous_document_doi_pairs):,}건이었다. 이를 모두 포함하면 정책문헌–논문 관계는 {int(quality.all_mapping_document_work_pairs):,}건, 기본 분석에서는 {p['document_work_pairs']:,}건이다. 두 값의 차이는 중복 제거와 다른 DOI를 통한 연결도 반영하므로, 제외한 DOI 관계 수와 같을 필요가 없다. 한 논문에만 연결되더라도 DOI나 메타데이터에 오류가 없음을 보장하지는 않는다.

### 연구 국가의 순차 부여

1저자의 기관 소재 국가를 사용한다. 기관 식별 정보 ROR의 국가 코드에서 가장 자주 나타나는 값을 먼저 선택한다. 같은 빈도이면 국가 코드 순으로 결정한다. ROR 국가를 찾지 못하면 OpenAlex 기관 국가 코드가 하나로 일치할 때만 보완하고, 나머지는 미부여로 남긴다. 연구 국가의 부여 단계별 [집계표]({LINK}/country_assignment.csv)와 [동률 집계표]({LINK}/country_ties.csv)를 제공한다.

2025 기준판의 보완 필드와 이번 스냅샷의 보완 필드는 다르다. 이번 OpenAlex에는 기존의 원문 소속 국가 코드 필드가 없어 OpenAlex 기관 국가 코드를 사용했다. 순차 부여 원칙을 유지하되 **동일한 필드를 사용한 재현은 아니다**. 아래 표는 ROR만 사용하거나 여러 논문에 연결되는 DOI를 포함했을 때 한국 정책문헌 지표가 어떻게 달라지는지 보여준다.

{table(sensitivity_ko,{'variant':'집계 조건','total_citations':'전체 인용','known_citations':'국가 확인 인용','us_share_known_pct':'미국 연구 %','kr_share_known_pct':'한국 연구 %'})}

### 2025 기준판과 최신판의 값·규칙 비교

{table(comparison_ko,{'indicator':'지표','baseline_2025':'2025 기준판','latest_202610':'2026년 10월 최신판'})}

| 집계 조건 | 2025 기준판 | 2026년 10월 최신판 |
|---|---|---|
| 자료 기준 | Overton 2025.02 · OpenAlex 2025.06 | Overton 2026-10-04 · OpenAlex 2026-06-25 |
| 인용 단위·DOI 연결 | 중복을 제거한 문헌–논문 관계 · 기존 매칭 입력 | 문헌–논문 관계 · 정규화 DOI를 새로 매칭하고 다중 논문 연결 DOI 제외 |
| 국가 보완 정보 | ROR 국가 우선 · 원문 소속 국가 코드로 보완 | ROR 국가 우선 · 단일 OpenAlex 기관 국가 코드로 보완 |
| 분야 비중의 기본 단위 | 도메인 부여 건수 | 도메인 부여 건수 |
| 최근 논문 창 | 2022–2024년 | 2023–2025년 · 미완결 2026년 제외 |

자료 수집 범위, DOI 대응 관계, 기관·국가 정보와 최근 논문 기준 연도가 함께 바뀌었다. 따라서 위 수치의 차이를 정책 인용 행태의 시계열 변화로 단정하지 않는다. 기대 비중은 이번에 비교 모집단과 가중 방식을 보완했으므로 위 표의 직접 비교 항목에서 제외했다.

### 공통 기관으로 범위를 좁히면

기준판 기관 집계표의 모든 기관 식별자와 최신판의 식별자를 정확히 대조했다. 두 판에 공통으로 나타난 기관은 {int(common.institutions):,}곳이다. 아래 표는 **모두 최신 스냅샷 안에서** 계산했으며, 전체 한국 출처와 공통 기관으로 제한한 표본을 비교한다. 마지막 행은 공통 기관의 정책문헌 중 발행연도가 2010–2024년인 문헌만 남겼다.

{table(scopes_ko,{'sample_scope':'분석 범위','citation_pairs':'인용 건수','social_share_pct':'사회과학 %','us_share_known_pct':'미국 연구 %','kdi_kiep_citation_share_pct':'KDI·KIEP %'})}

사회과학 비중은 도메인 부여 건수, 미국 연구 비중은 국가 확인 인용, KDI·KIEP 비중은 해당 범위의 전체 인용이 기준이다. 공통 기관의 사회과학 비중은 **{common.social_share_pct:.1f}%**였다. 동일 기관을 제한해도 문헌 구성·DOI 매칭·OpenAlex 메타데이터까지 같아지는 것은 아니다. 기관 식별자가 바뀐 경우의 대응은 추정하지 않았다. [기관별 대조표]({LINK}/korea_common_institutions.csv)는 범위 확인용이며 기관별 증감률의 근거로 사용하지 않는다.

## 7. 집계표와 다음 점검 {{#update-downloads}}

- [공개 집계표·그림 생성 코드 묶음]({LINK}/online_update_aggregates.zip) · [그림 생성 코드]({LINK}/plot_online_update_202610.py) · [이용 안내]({LINK}/README_KO.md)
- [자료 규모]({LINK}/data_profile.csv) · [DOI 연결 점검]({LINK}/doi_linkage_audit.csv)
- [한국 연구를 인용한 정책 출처]({LINK}/korea_inbound_sources.csv) · [한국 정책문헌이 인용한 연구 국가]({LINK}/korea_outbound_countries.csv) · [두 방향의 분야 구성]({LINK}/direction_domains.csv)
- [정책 출처별 집계]({LINK}/policy_sources.csv) · [출처 유형별 집계]({LINK}/source_types.csv) · [토픽별 지표]({LINK}/topic_metrics.csv) · [연구 발행연도별 집계]({LINK}/publication_year.csv)
- [국가 부여 민감도]({LINK}/korea_country_sensitivity.csv) · [기대 비중]({LINK}/korea_expected_country_shares.csv) · [입력 스냅샷·체크섬·집계 규칙]({LINK}/provenance.json)
- [분야 가중 방식 민감도]({LINK}/korea_domain_weighting_sensitivity.csv) · [기관별 분야 구성]({LINK}/korea_institution_domains.csv) · [방향별 출처 집단 구성]({LINK}/korea_direction_source_groups.csv)
- [기대 비중 계산 조건 비교]({LINK}/korea_expected_country_variants.csv) · [관측·기대 비교 모집단]({LINK}/korea_expected_country_population.csv) · [기준판·최신판 지표 비교]({LINK}/edition_indicator_comparison.csv) · [공통 기관 제한 집계]({LINK}/korea_common_institution_scopes.csv)

다음 점검에서는 공통 기관에 더해 정책문헌 ID와 논문 메타데이터·연결 규칙까지 고정한 비교가 필요하다. DOI가 없는 국내 참고문헌을 포함하려면 NKIS 등 국내 정책문헌의 참고문헌 연결을 별도로 구축해야 한다.
'''
    (ROOT/'Data_Insight/SI/update_202603.qmd').write_text(number_captions(ko,'ko'))
    en=f'''---
title: "October 2026 Data Update"
description: "Recomputed online results using Overton 2026-10-04 and OpenAlex 2026-06-25."
format:
  html:
    lang: en
    language: en
---

[English baseline summary](index_en.qmd) · [Full Korean update](update_202603.qmd) · [2025 Korean report PDF](../Report/Report_final.pdf)

**Updated:** 8 October 2026 · **Overton:** 2026-10-04 · **OpenAlex:** 2026-06-25

::: {{.callout-note}}
This page reports the new online analysis. The linked report PDF and the other methods, appendix and interactive pages describe the 2025 baseline edition. The analysis covers observed DOI-linked policy-document → research citations, restricted to DOIs mapping to one OpenAlex work.
:::

## Korea's two citation directions

The top three policy-source categories account for **{top3:.1f}%** of source-tagged citations to Korean research. Among citations from Korean policy documents with an assigned research country, U.S. research accounts for **{us:.1f}%** and Korean research for **{kr:.1f}%**. These percentages describe different populations and directions.

| Indicator | Updated value |
|---|---:|
| Unique policy-document/work pairs | {p['document_work_pairs']:,} |
| Citing policy documents | {p['citing_policy_documents']:,} |
| Cited unique works | {p['cited_works']:,} |
| Citations from Korean policy documents | {total:,} |
| Research-country missingness in Korean policy citations | {missing:.1f}% |
| Social sciences: Korean policy → research | {socialout:.1f}% |
| Social sciences: policy → Korean research | {socialin:.1f}% |
| Health sciences: Korean policy → research | {healthout:.1f}% |
| Health sciences: policy → Korean research | {healthin:.1f}% |
| KDI/KIEP share of citations from Korean policy documents | {institutional:.1f}% |
| Cited works appearing in at least two different policy documents | {repeat:.1f}% |

![Korea's two citation directions. Left: shares of source-tagged citations to Korean research. Right: research-country shares among citations from Korean policy documents with a known country. Top ten shown.]({FIG}/korea_flows.png)

{embed('korea_flows',"Korea's two citation directions: countries",'en')}

![Domain composition by direction. Each work/domain pair is counted once; different domains on the same work are included separately. Shares are normalized over domain assignments within each direction.]({FIG}/korea_domains.png)

{embed('korea_domains',"Korea's two citation directions: domains",'en')}

## Aligned observed and expected country shares

The comparison is restricted to **{int(eligible.eligible_citation_pairs):,} Korean-policy citation pairs with both an assigned research country and a domain**. It excludes {int(eligible.all_country_known_pairs-eligible.eligible_citation_pairs):,} otherwise country-known pairs without domains. Each citation's weight is split equally across its distinct assigned domains, so its total weight is one. The reference country profile within each domain uses cited unique works with an assigned country in the joined sample.

On exactly this eligible population, the U.S. observed share is **{expected_observed:.1f}%** and the expected share is **{expected:.1f}%**, a difference of **{expected_observed-expected:.1f} percentage points**. This is a descriptive reference, not total OpenAlex research production or a policy target. Figure 1 includes all country-known citations, whether or not domains are available. The [calculation variants]({LINK}/korea_expected_country_variants.csv), [domain weights]({LINK}/korea_expected_domain_weights.csv), [domain-country reference profiles]({LINK}/expected_country_domain_reference.csv) and [eligible population]({LINK}/korea_expected_country_population.csv) make the scope and arithmetic explicit.

## Domain weighting sensitivity

{table(weighting_en,{'variant':'Weighting','out':'Korean policy → research %','in':'Policy → Korean research %','gap':'Social-science gap, pp'})}

Both share columns refer to social sciences. Document-equal weighting averages each document's social-science share of full domain assignments, among documents with domains. Distinct-work weighting counts each work/domain once within each direction. Fractional weighting splits a citation's unit weight across its assigned domains. The gap remains positive across all four definitions, ranging from **{weighting.gap.min():.1f} to {weighting.gap.max():.1f} percentage points**; this is a range across definitions, not a confidence interval.

## Institutions and source-group composition

{table(institution_display_en,{'policy_source_title':'Institution','citation_rows':'Citation pairs','policy_documents':'Citing documents','share_pct':'Social sciences %'})}

These are the ten largest Korean institutions by citation count plus KDI/KIEP. Social-science shares use full domain assignments within institutions. Original names and identifiers remain in the downloadable aggregates.

{table(groups_en,{'direction':'Direction','source_group':'Source group','domain_weight_pct':'Group weight %','social_share_pct':'Within-group social sciences %'})}

Documents with any top-level think-tank tag form one exclusive group; all remaining documents, including unassigned types, form the other. There are {int(source_groups.unassigned_type_pairs.sum()):,} type-unassigned citation pairs in these two directions. Group weights use domain assignments. A symmetric descriptive decomposition of the **{socialout-socialin:.1f} pp** social-science gap attributes **{composition_pp:.1f} pp** to the source-group composition term and **{within_pp:.1f} pp** to the within-group share term. This is an arithmetic decomposition, not a causal attribution. The terms are respectively the sum of group-weight differences times mean within-group shares, and within-group share differences times mean group weights across the two directions. [Group-level decomposition]({LINK}/korea_source_group_decomposition.csv).

## Baseline comparison and common institutions

{table(comparison,{'indicator':'Indicator','baseline_2025':'2025 baseline','latest_202610':'October 2026'})}

Percent indicators are on a 0–100 scale. The baseline uses Overton February 2025 and OpenAlex June 2025, the existing DOI matching input, ROR with raw-affiliation country fallback, full domain assignments and a 2022–2024 recent-work window. The latest uses the snapshots above, freshly normalized DOI matching excluding multi-work matches, ROR with single-institution-country fallback, full domain assignments and a 2023–2025 recent-work window. Expected shares are omitted from this comparison because the population and weighting were refined here.

Exact source identifiers intersect in **{int(common.institutions):,} institutions**. The following rows all use the **latest snapshot**, comparing its full Korean source sample with restrictions to common institutions and to policy documents published in 2010–2024.

{table(scopes,{'sample_scope':'Latest-snapshot scope','citation_pairs':'Citation pairs','social_share_pct':'Social sciences %','us_share_known_pct':'U.S. research %','kdi_kiep_citation_share_pct':'KDI/KIEP %'})}

Social-science shares use domain assignments, U.S. shares country-known citations, and KDI/KIEP shares all citations in each scope. Restricting institutions does not fix document identity, DOI mapping or OpenAlex metadata. Renamed identifiers are not inferred. These are coverage comparisons, not estimates of behavioral change. [Institution-ID crosswalk]({LINK}/korea_common_institutions.csv).

## Data linkage and comparability

- {int(quality.matched_dois):,} of {int(quality.unique_dois):,} unique DOIs match OpenAlex. The {int(quality.ambiguous_dois):,} DOIs mapping to multiple work IDs are excluded from the primary analysis; an unrestricted-mapping sensitivity table is available.
- First-author country uses the mode of ROR country codes by affiliation-row frequency, with alphabetical ties. If unavailable, a single unambiguous OpenAlex institution country code is accepted. Unresolved works remain unassigned.
- The 2025 baseline used a different fallback field. Snapshot coverage, DOI disambiguation and the fallback field all changed, so differences from the baseline must not be interpreted directly as behavioral trends.
- The recent-work window is 2023–2025 among works with a known publication year up to 2025. Incomplete 2026 is excluded. This differs from the baseline's 2022–2024 window.
- Policy-source tags may overlap; citation counts do not measure causal policy impact.

## Interactive figures and downloads

### Policy-source totals and averages

![Citation totals and citations per citing policy document for the same top ten policy sources, ranked by citation totals.]({FIG}/policy_sources.png)

{embed('policy_sources','Policy-source totals and averages','en')}

### Domains by source type

![Domain shares within each of the seven policy-source types with the most domain assignments. Each source type sums to 100%.]({FIG}/source_type_domains.png)

{embed('source_type_domains','Domains by policy-source type','en')}

### Topic metrics

![Citations per cited work and the share of cited unique works published in 2023–2025 for the top 300 topics by citations. The recent-work share uses works with a known publication year up to 2025.]({FIG}/topic_intensity_recency.png)

{embed('topic_intensity_recency','Topic citation intensity and recent-work share','en')}

### Publication years

![Citations by publication year of cited research, 1990–2026. The shaded 2026 interval is incomplete; this is not a series by policy-document publication year.]({FIG}/research_publication_year.png)

{embed('research_publication_year','Publication years of cited research','en')}

[Public aggregates and source code]({LINK}/online_update_aggregates.zip) · [Data profile]({LINK}/data_profile.csv) · [DOI audit]({LINK}/doi_linkage_audit.csv) · [Domain aggregates]({LINK}/direction_domains.csv) · [Country sensitivity]({LINK}/korea_country_sensitivity.csv) · [Weighting sensitivity]({LINK}/korea_domain_weighting_sensitivity.csv) · [Institution domains]({LINK}/korea_institution_domains.csv) · [Source groups]({LINK}/korea_direction_source_groups.csv) · [Edition comparison]({LINK}/edition_indicator_comparison.csv) · [Common-institution scopes]({LINK}/korea_common_institution_scopes.csv) · [Provenance]({LINK}/provenance.json)

See the [full Korean update](update_202603.qmd) for institution tables, source totals and averages, publication-year distributions and follow-up questions.
'''
    (ROOT/'Data_Insight/SI/update_202603_en.qmd').write_text(number_captions(en,'en'))
    summary=dict(top3=top3,us=us,kr=kr,missing=missing,repeat=repeat,socialout=socialout,socialin=socialin,
                 healthout=healthout,healthin=healthin,socialgap=socialout-socialin,expected=expected,
                 institutional=institutional,source_names=source_names,expected_observed=expected_observed,
                 expected_eligible_pairs=int(eligible.eligible_citation_pairs),
                 weighting_gap_min=weighting.gap.min(),weighting_gap_max=weighting.gap.max(),
                 composition_pp=composition_pp,within_pp=within_pp,
                 common_institution_social_share=common.social_share_pct)
    (DATA/'headline_metrics.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
