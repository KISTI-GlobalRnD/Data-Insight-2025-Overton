# 2026년 10월 온라인 업데이트 집계표

Overton 2026-10-04와 OpenAlex 2026-06-25를 결합한 온라인 분석의 공개 집계표다. Overton 원자료·문헌별 인용·개별 연구 레코드는 포함하지 않는다.

- DOI 정규화: 소문자로 통일하고 공백과 보이지 않는 Unicode 서식 문자를 제거한다.
- 인용 단위: 한 정책문헌–한 OpenAlex 논문 관계. 여러 논문에 대응하는 DOI는 기본 분석에서 제외한다.
- 연구 국가: 1저자 ROR 국가 코드의 빈도 최빈값, 동률 시 코드 순. ROR 국가가 없으면 단일 OpenAlex 기관 국가 코드로 보완한다.
- 도메인: 한 논문의 같은 도메인은 한 번만 세며, 여러 도메인은 각각 포함한다.
- 최근 논문: 발행연도가 확인되는 2025년 이하 고유 논문 가운데 2023–2025년 발행 논문.
- 정책 출처 태그는 상호 배타적이지 않을 수 있다. 국가 비중은 국가가 확인되는 인용을 기준으로 한다.

## 주요 파일

`doi_linkage_audit.csv`: 원자료·DOI 매칭·다중 연결 DOI 제외의 규모.
`data_profile.csv`: 최종 분석 모집단과 결측 규모.
`korea_inbound_sources.csv`, `korea_outbound_countries.csv`: 한국의 두 인용 방향.
`direction_domains.csv`: 두 방향의 도메인 구성.
`korea_institutions.csv`: 한국 정책문헌의 기관 구성.
`korea_country_sensitivity.csv`: 다중 연결 DOI 포함 및 ROR만 사용한 민감도.
`topic_metrics.csv`: 토픽별 인용 총량·고유 논문·최근 논문 비중.
`provenance.json`: 스냅샷·입력 체크섬·집계 규칙·집계표 체크섬.

2025 기준 보고서와 집계 규칙·자료 범위·국가 보완 필드·최근 논문 창이 다르므로 수치 차이를 행태 변화로 단정하지 않는다. 웹 본문은 같은 폴더의 CSV에서 생성된다. 원자료 전체 재분석에는 별도의 이용 권한과 로컬 입력, 해당 OpenAlex DB의 읽기 권한이 필요하다.

## 원자료 없이 그림 다시 만들기

공개 묶음을 푼 폴더에서 pandas, numpy, matplotlib, plotly가 설치된 Python을 사용한다.

```bash
python plot_online_update_202610.py --data-dir . --out-dir figures --html-dir interactive
```

그림 코드는 이 폴더의 CSV를 읽는다. 공개 집계표의 산술 재확인·그림 재생성과 이용 조건이 있는 원자료 전체 재수집은 구분한다.

정적 그림 6개와 같은 집계표·선택 조건을 사용하는 인터랙티브 그림 6개를 함께 생성한다. 그림의 국가 표시는 영문 국가명으로 통일하며, 한국의 두 인용 방향별 분야 비중 그림은 가로축을 0–70%로 표시한다. 출처 유형별 누적 비중 그림은 0–100%를 유지한다.


## 2026-10-08 추가 분석

- `korea_expected_country_population.csv`: 관측·기대 국가 비중을 비교하는 국가·분야 확인 인용 모집단. 그림 1의 국가 확인 인용 전체와 구분한다.
- `korea_expected_country_variants.csv`, `korea_expected_domain_weights.csv`, `expected_country_domain_reference.csv`: 이전 계산·국가 확인 자료 제한·인용별 분할 가중의 세 가지 기대 비중과 산술 재현용 가중치·분야별 국가 구성. `korea_expected_country_shares.csv`는 마지막 방식을 채택한다.
- `korea_domain_weighting_sensitivity.csv`: 인용–도메인, 고유 논문–도메인, 문헌 동일 가중, 인용별 도메인 분할 가중의 네 가지 분야 구성. `weight`·`total_weight`는 각각 집계된 가중치와 방향별 합계이며 `share_pct = 100 × weight / total_weight`다. 도메인이 없는 관측은 제외한다.
- `korea_institution_domains.csv`: 기관별 도메인 부여 건수와 비중.
- `korea_direction_source_groups.csv`, `korea_source_group_decomposition.csv`: 두 인용 방향의 배타적 싱크탱크/그 외 출처 집단 구성과 사회과학 격차의 대칭 산술 분해. 유형 미부여는 그 외 집단에 포함한다. 정책 효과나 인과적 설명을 뜻하지 않는다.
- `edition_indicator_comparison.csv`: 기준판·최신판의 주요 값. 기준판은 Overton 2025.02·OpenAlex 2025.06이며 `20251026`은 기존 집계 파일의 실행 태그다. 규칙과 관측 범위가 달라 단순 증감률을 계산하지 않는다.
- `korea_common_institutions.csv`, `korea_common_institution_scopes.csv`: 기존 기관 집계표 전체의 식별자와 정확히 일치하는 공통 기관, 그리고 최신 스냅샷 안에서 공통 기관·발행연도를 제한한 결과. 기관명이 바뀐 경우의 대응은 추정하지 않는다. 구판과 신판의 정책문헌 ID·DOI 연결·연구 메타데이터를 모두 고정한 시계열 비교는 아니다.

기대 비중은 해당 variant의 분야 가중치 비중과 분야별 국가 구성비를 곱해 분야별로 합하면 재현된다. 출처 구성 분해는 두 방향의 출처 집단 가중치를 w, 집단 내 사회과학 비중을 p로 두고 `Σ(w_out − w_in) × (p_out + p_in) / 2`와 `Σ(p_out − p_in) × (w_out + w_in) / 2`를 합한다. 각 비중을 0–1로 변환해 계산한 뒤 100을 곱하면 %p다.

`analyze_online_update_202610.py`, `refine_online_update_202610.py`는 저장소의 원자료 분석 코드 사본이다. 코드의 파일 경로는 저장소 구조와 권한이 있는 로컬 입력을 전제로 한다. 전체 분석은 저장소 `scripts/`에서 실행하며, 집계 스크립트는 끝에서 보완 분석을 호출한다. 이미 유효한 `local_runs/.../analysis.duckdb`가 있으면 보완 스크립트만 실행할 수 있다. 공개 ZIP에는 원자료·DB·문헌별 연결을 넣지 않았다. 공개 CSV만으로 가능한 작업은 그림 재생성, 기대 비중·분해의 산술 검산이다.


저장소에서 보완 분석을 실행한 뒤 `write_online_update_202610.py` → `update_online_landing_202610.py` → `package_online_update_202610.py` → `quarto render Data_Insight --no-clean` 순서로 본문·메인·다운로드·사이트를 맞춘다. 묶음의 본문·메인·패키징 코드 사본도 저장소 경로를 전제로 한다. 패키징은 집계표의 체크섬이 계산 결과와 일치하는지 확인하고 현재 코드·웹 원문의 체크섬을 기록한다.
