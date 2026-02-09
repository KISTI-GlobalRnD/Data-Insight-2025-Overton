(function () {
  "use strict";

  const STORAGE_KEYS = ["promo_lang", "si_lang"];
  const SUPPORTED = ["ko", "en"];

  const KO = {
    // Plot titles
    "Policy citations by policy source country (top 10 + Republic of Korea)": "정책 출처 국가별 정책 인용(상위 10 + 한국)",
    "Selected countries (top 50): domain mix mismatch (demand vs supply)": "선택 국가(상위 50): 도메인 구성 불일치(수요 vs 공급)",
    "Domain composition of policy citations (top 10 + Republic of Korea)": "정책 출처 국가별 도메인 구성(상위 10 + 한국)",
    "Overton coverage: policy documents by policy source country (log10 scale)": "Overton 커버리지: 정책 출처 국가별 정책문헌 수(log10)",
    "Policy citations by domain (top 4; stacked by field)": "도메인별 정책 인용(상위 4; 분야별 누적)",
    "Republic of Korea evidence flows and domain portfolios (top 10; DOI-matched, first-author country)":
      "한국 근거 흐름과 도메인 포트폴리오(상위 10; DOI 매칭, 1저자 국가)",
    "Self-citation share vs expected and domain portfolio (top 7 policy countries + Republic of Korea)":
      "자국 인용 비중(관측 vs 기대)과 도메인 구성(상위 7 + 한국)",
    "Policy–research evidence flows (top 3 imports/exports per node)": "정책-연구 근거 흐름(노드당 상위 3 유입/유출)",
    "Policy source → Research country citations": "정책 출처 → 연구국 인용",
    "Policy documents by publication year (DOI citations)": "발행연도별 정책문헌(DOI 인용)",
    "Citations per policy document by policy source type (selected types)": "출처 유형별 문헌당 평균 인용(선택 유형)",
    "Citations by policy source type (top 10)": "출처 유형별 총 인용(상위 10)",
    "Share heatmap: domain × policy source type (selected; source-type normalized)":
      "비중 히트맵: 도메인 × 출처 유형(선택; 출처 유형 내 정규화)",
    "Topics: intensity vs recency (color=domain)": "토픽: 인용 강도 vs 최근성(색=도메인)",
    "Topics: citations vs unique papers (size=OA share)": "토픽: 정책 인용 vs 고유 논문 수(크기=OA 비중)",

    // Axes / legend labels
    Citations: "인용(건수)",
    "Policy source country": "정책 출처 국가",
    "Citations per policy document": "정책문헌당 평균 인용",
    "Share within policy source (normalized)": "출처 내부 비중(정규화)",
    "Cited research share by domain": "피인용 연구 비중(도메인별)",
    "Policy citations share by domain": "정책 인용 비중(도메인별)",
    "Country (click to toggle)": "국가(클릭으로 토글)",
    Domain: "도메인",
    domain: "도메인",
    "Policy source entity": "정책 출처",
    "Policy citations": "정책 인용(건수)",
    "Policy documents": "정책문헌 수",
    "Publication year (policy documents)": "발행연도(정책문헌)",
    "Citations per document": "문헌당 평균 인용",
    "Share (%)<br>(first-author country available only)": "비중(%)<br>(1저자 국가코드 확인 건만)",
    "Actual − expected (pp)<br>(domain-weighted baseline)": "관측 − 기대(pp)<br>(도메인 가중 기준선)",
    "Citations to KR research": "한국 연구로의 인용",
    "Citations from KR policy<br>(first-author country available only)": "한국 정책의 인용<br>(1저자 국가코드 확인 건만)",
    "Share within inbound flow (normalized)": "유입 흐름 내부 비중(정규화)",
    "Share within outbound flow (normalized)": "유출 흐름 내부 비중(정규화)",
    "Source type": "출처 유형",
    "Policy source type": "출처 유형",
    "Unique papers (log)": "고유 논문 수(log)",
    "Citations (log)": "정책 인용(log)",
    "Citations per paper": "논문당 정책 인용",
    "Recent share (2022–24)": "최근성(2022–24 비중)",

    // Annotations
    "A. Total citations": "A. 총 인용",
    "B. Citations per policy doc": "B. 문헌당 평균 인용",
    "C. Domain composition": "C. 도메인 구성",
    "A. Policy sources citing KR first-author research": "A. 한국 1저자 연구를 인용하는 정책 출처",
    "B. Research countries cited by Republic of Korea policy": "B. 한국 정책이 인용하는 연구국",
    "C. Domain mix of cited research (KR vs non-KR)": "C. 피인용 연구 도메인 구성(한국 vs 비한국)",
    "D. Domain mix of cited research (KR vs non-KR policy)": "D. 피인용 연구 도메인 구성(한국 정책 vs 비한국 정책)",
    "A. Self-citation share": "A. 자국 인용 비중",
    "B. Self-citation vs expected": "B. 자국 인용(관측 vs 기대)",
    "C. Domain composition of cited research": "C. 피인용 연구 도메인 구성",
    "Overall: 32.7%": "전체: 32.7%",
    "A. Absolute citations (log10 scale)": "A. 절대 인용(log10)",
    "B. Row-normalized share (cap at 30%)": "B. 행 정규화 비중(최대 30% 절단)",

    // Trace names / categories (keep this list intentionally small)
    "Policy citations (count)": "정책 인용(건수)",
    "Policy documents (with DOI citations)": "정책문헌 수(DOI 인용 포함)",
    "Citations per policy document": "정책문헌당 평균 인용",
    "Social Sciences": "사회과학",
    "Health Sciences": "보건/의학",
    "Physical Sciences": "물리/공학",
    "Life Sciences": "생명과학",
    Unknown: "미분류",
    Other: "기타",
    "Republic of Korea": "한국",
    "Policy source": "정책 출처",
    "Republic of Korea (highlight)": "한국(강조)",
    Both: "양방향",
    "Node type": "노드 유형",
    "Total flow": "총 흐름",
    "A. Total flow": "A. 총 흐름",
    "B. Top neighbors": "B. 주요 이웃",
    "C. Selected node": "C. 선택 노드"
  };

  const STYLE_ID = "plot-i18n-style";

  function isSupported(lang) {
    return SUPPORTED.includes(lang);
  }

  function getParamLang() {
    try {
      const url = new URL(window.location.href);
      const raw = (url.searchParams.get("lang") || "").toLowerCase();
      return isSupported(raw) ? raw : null;
    } catch (_err) {
      return null;
    }
  }

  function getSavedLang() {
    for (const k of STORAGE_KEYS) {
      try {
        const v = window.localStorage.getItem(k);
        if (isSupported(v)) return v;
      } catch (_err) {
        // ignore
      }
    }
    return null;
  }

  function getPreferredLang() {
    return getParamLang() || getSavedLang() || ((navigator.language || "").toLowerCase().startsWith("en") ? "en" : "ko");
  }

  function setPreferredLang(lang) {
    const safe = isSupported(lang) ? lang : "ko";
    for (const k of STORAGE_KEYS) {
      try {
        window.localStorage.setItem(k, safe);
      } catch (_err) {
        // ignore
      }
    }
  }

  function translate(str, lang) {
    if (lang !== "ko") return str;
    if (typeof str !== "string") return str;
    return Object.prototype.hasOwnProperty.call(KO, str) ? KO[str] : str;
  }

  function ensureStyle() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = `
      :root {
        --plot-switch-border: rgba(0, 0, 0, 0.14);
        --plot-switch-bg: rgba(255, 255, 255, 0.72);
        --plot-switch-text: rgba(17, 24, 39, 0.72);
        --plot-switch-text-strong: rgba(17, 24, 39, 0.92);
        --plot-switch-active-bg: rgba(17, 24, 39, 0.10);
        --plot-focus: rgba(37, 99, 235, 0.85);
      }

      .plot-lang-switch {
        position: fixed;
        top: 0.85rem;
        left: 0.9rem;
        z-index: 9999;
        display: inline-flex;
        gap: 0.25rem;
        padding: 0.25rem;
        border-radius: 999px;
        border: 1px solid var(--plot-switch-border);
        background: var(--plot-switch-bg);
        backdrop-filter: blur(10px);
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
      }

      .plot-lang-btn {
        appearance: none;
        border: none;
        border-radius: 999px;
        padding: 0.48rem 0.76rem;
        background: transparent;
        color: var(--plot-switch-text);
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-size: 0.78rem;
        cursor: pointer;
        text-decoration: none;
        line-height: 1;
      }

      .plot-lang-btn:hover {
        background: rgba(17, 24, 39, 0.06);
        color: var(--plot-switch-text-strong);
      }

      .plot-lang-btn.is-active {
        background: var(--plot-switch-active-bg);
        color: var(--plot-switch-text-strong);
      }

      .plot-lang-btn:focus-visible {
        outline: 2px solid var(--plot-focus);
        outline-offset: 2px;
      }

      @media (max-width: 640px) {
        .plot-lang-switch {
          top: 0.65rem;
          left: 0.65rem;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function getGraphDiv() {
    return document.querySelector(".plotly-graph-div");
  }

  function snapshotLayoutText(layout, keyPath) {
    const parts = keyPath.split(".");
    let cur = layout;
    for (const p of parts) {
      if (!cur || typeof cur !== "object" || !(p in cur)) return null;
      cur = cur[p];
    }
    return typeof cur === "string" ? cur : null;
  }

  function setDeep(obj, keyPath, value) {
    const parts = keyPath.split(".");
    const last = parts.pop();
    if (!last) return;
    let cur = obj;
    for (const p of parts) {
      if (!cur[p] || typeof cur[p] !== "object") cur[p] = {};
      cur = cur[p];
    }
    cur[last] = value;
  }

  function captureBaseline(gd) {
    if (gd.__plotI18nBaseline) return gd.__plotI18nBaseline;

    const base = { layout: {}, axes: {}, annotations: [], traces: [] };
    const layout = gd.layout || {};

    base.layout["title.text"] = snapshotLayoutText(layout, "title.text");
    base.layout["legend.title.text"] = snapshotLayoutText(layout, "legend.title.text");

    // Axis titles + category arrays (strings only)
    Object.keys(layout).forEach((k) => {
      if (!/^[xy]axis\\d*$/.test(k)) return;
      const axis = layout[k];
      if (!axis || typeof axis !== "object") return;
      const t = snapshotLayoutText(axis, "title.text");
      if (t) base.axes[`${k}.title.text`] = t;
      if (Array.isArray(axis.categoryarray) && axis.categoryarray.every((v) => typeof v === "string")) {
        base.axes[`${k}.categoryarray`] = axis.categoryarray.slice();
      }
    });

    // Annotation texts
    if (Array.isArray(layout.annotations)) {
      base.annotations = layout.annotations.map((a) => (a && typeof a.text === "string" ? a.text : null));
    }

    // Trace names, legend group titles, and categorical y arrays (strings only)
    (gd.data || []).forEach((tr) => {
      const rec = {
        name: typeof tr.name === "string" ? tr.name : null,
        legendgrouptitle: tr.legendgrouptitle && typeof tr.legendgrouptitle.text === "string" ? tr.legendgrouptitle.text : null,
        y: Array.isArray(tr.y) && tr.y.every((v) => typeof v === "string") ? tr.y.slice() : null,
      };
      base.traces.push(rec);
    });

    gd.__plotI18nBaseline = base;
    return base;
  }

  function applyLanguageToPlot(gd, lang) {
    if (!gd || !window.Plotly) return;
    const safe = isSupported(lang) ? lang : "ko";
    const base = captureBaseline(gd);

    const layoutUpdates = {};

    // Layout title + legend title
    if (base.layout["title.text"]) layoutUpdates["title.text"] = translate(base.layout["title.text"], safe);
    if (base.layout["legend.title.text"]) layoutUpdates["legend.title.text"] = translate(base.layout["legend.title.text"], safe);

    // Axes
    Object.keys(base.axes).forEach((k) => {
      const v = base.axes[k];
      if (Array.isArray(v)) layoutUpdates[k] = v.map((s) => translate(s, safe));
      else layoutUpdates[k] = translate(v, safe);
    });

    // Annotations (keep array shape)
    base.annotations.forEach((t, idx) => {
      if (typeof t !== "string") return;
      layoutUpdates[`annotations[${idx}].text`] = translate(t, safe);
    });

    try {
      window.Plotly.relayout(gd, layoutUpdates);
    } catch (_err) {
      // ignore
    }

    // Traces: update only when needed (compare against current plot state).
    base.traces.forEach((tr, idx) => {
      if (!tr) return;
      const cur = (gd.data || [])[idx] || {};
      if (typeof tr.name === "string") {
        const nextName = translate(tr.name, safe);
        if (typeof cur.name === "string" && cur.name !== nextName) {
          try {
            window.Plotly.restyle(gd, { name: nextName }, [idx]);
          } catch (_err) {
            // ignore
          }
        }
      }

      if (typeof tr.legendgrouptitle === "string") {
        const nextTitle = translate(tr.legendgrouptitle, safe);
        const curTitle = cur.legendgrouptitle && typeof cur.legendgrouptitle.text === "string" ? cur.legendgrouptitle.text : null;
        if (curTitle && curTitle !== nextTitle) {
          try {
            window.Plotly.restyle(gd, { legendgrouptitle: [{ text: nextTitle }] }, [idx]);
          } catch (_err) {
            // ignore
          }
        }
      }

      if (Array.isArray(tr.y)) {
        const nextY = tr.y.map((s) => translate(s, safe));
        // Only restyle if there is at least one change.
        const curY = Array.isArray(cur.y) ? cur.y : null;
        const comparable = curY && curY.length === nextY.length && curY.every((v) => typeof v === "string");
        let changed = !comparable;
        if (comparable) {
          for (let i = 0; i < nextY.length; i++) {
            if (curY[i] !== nextY[i]) {
              changed = true;
              break;
            }
          }
        }
        if (changed) {
          try {
            window.Plotly.restyle(gd, { y: [nextY] }, [idx]);
          } catch (_err) {
            // ignore
          }
        }
      }
    });
  }

  function insertLangSwitch(initialLang, onChange) {
    if (window.self !== window.top) return;
    ensureStyle();

    const existing = document.querySelector(".plot-lang-switch");
    if (existing) return;

    const wrapper = document.createElement("div");
    wrapper.className = "plot-lang-switch";
    wrapper.setAttribute("role", "group");
    wrapper.setAttribute("aria-label", "Language");

    const korBtn = document.createElement("button");
    korBtn.type = "button";
    korBtn.className = "plot-lang-btn";
    korBtn.dataset.lang = "ko";
    korBtn.textContent = "KOR";

    const enBtn = document.createElement("button");
    enBtn.type = "button";
    enBtn.className = "plot-lang-btn";
    enBtn.dataset.lang = "en";
    enBtn.textContent = "ENG";

    function setButtons(active) {
      [korBtn, enBtn].forEach((btn) => {
        const isActive = btn.dataset.lang === active;
        btn.classList.toggle("is-active", isActive);
        btn.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
    }

    wrapper.addEventListener("click", (event) => {
      const btn = event.target.closest("button[data-lang]");
      if (!btn) return;
      event.preventDefault();
      const next = btn.dataset.lang;
      if (!isSupported(next)) return;
      setPreferredLang(next);
      setButtons(next);
      onChange(next);
    });

    wrapper.appendChild(korBtn);
    wrapper.appendChild(enBtn);
    document.body.appendChild(wrapper);

    setButtons(initialLang);
  }

  function init() {
    const gd = getGraphDiv();
    if (!gd || !window.Plotly) return;

    const initial = getPreferredLang();
    setPreferredLang(initial);

    function apply(lang) {
      applyLanguageToPlot(gd, lang);
    }

    // Apply once the plot is ready; some exports (esp. networks) are async.
    let applied = false;
    function maybeApply() {
      if (applied) return;
      if (gd.data && gd.layout) {
        applied = true;
        apply(initial);
      }
    }

    // Try now, and also retry on next frames.
    maybeApply();
    if (typeof gd.on === "function") {
      try {
        gd.on("plotly_afterplot", () => {
          if (!applied) maybeApply();
        });
      } catch (_err) {
        // ignore
      }
    }
    let tries = 0;
    (function tick() {
      if (applied) return;
      tries += 1;
      if (tries > 120) return; // ~2s at 60fps
      requestAnimationFrame(() => {
        maybeApply();
        tick();
      });
    })();

    insertLangSwitch(initial, (lang) => {
      apply(lang);
    });

    window.addEventListener("message", (event) => {
      try {
        if (event.origin !== window.location.origin) return;
      } catch (_err) {
        return;
      }
      const msg = event.data || {};
      if (!msg || msg.type !== "si:setLang") return;
      const lang = (msg.lang || "").toLowerCase();
      if (!isSupported(lang)) return;
      setPreferredLang(lang);
      apply(lang);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
