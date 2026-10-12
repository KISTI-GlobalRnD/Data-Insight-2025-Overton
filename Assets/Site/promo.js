(function () {
  "use strict";

  try {
    if ("scrollRestoration" in window.history) window.history.scrollRestoration = "manual";
  } catch (_err) {
    // Ignore; fallback to browser defaults.
  }

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const LANG_STORAGE_KEY = "promo_lang";
  const SUPPORTED_LANGS = ["ko", "en"];
  const baseline = new WeakMap();

  const en = {
    "hero.stat.gap.value": "41.1 pp",
    "hero.cta.report.href": "./SI/update_202603_en.html",
    "meta.title": "Korea's Policy–Research Citations | Overton × OpenAlex",
    "meta.description":
      "A concise comparison of policy sources citing Korean research and research countries and fields cited by Korean policy documents.",
    "skip.link": "Skip to content",
    "lang.aria": "Language",
    "hero.kicker": "October 2026 Online Update",
    "hero.title": "Who cites Korean research, and whose research do Korean policy documents cite?",
    "hero.lede":
      "Social sciences account for 64.2% of domain assignments in research cited by Korean policy documents, compared with 23.1% in Korean research cited by policy documents.",
    "hero.lede2":
      "This page presents the <strong>October 2026 online results</strong> for DOI-linked citations from policy documents to research. Each DOI must map to a single OpenAlex work. The analysis does not cover every policy document or reference. The linked PDF and baseline supplements describe the <strong>2025 edition</strong>. Research country refers to the first author’s institutional affiliation, not nationality.",
    "hero.actions.aria": "Quick links",
    "hero.cta.report": "Read Latest Online Results",
    "hero.cta.si": "Read 2025 Baseline Summary",
    "hero.cta.si.href": "./SI/index_en.html",
    "hero.stats.aria": "Main numbers",
    "hero.stat.inbound": "Combined share of the top 3 policy sources citing Korean research",
    "hero.stat.sourcing": "U.S. research share among citations from Korean policy documents with an assigned research country",
    "hero.stat.repeat": "Difference in social-science share between the two citation directions",
    "hero.meta.snapshot": "Snapshots: Overton 2026-10-04 · OpenAlex 2026-06-25 · Distinct policy document–work citations",
    "hero.scroll": "Scroll",
    "story.kicker": "Main Comparisons",
    "story.title": "Four views of research cited by policy documents",
    "story.progress.label": "Item",
    "story.steps.aria": "Analysis items",
    "fig.hub_country.alt": "October 2026: policy-source citation totals and averages per citing document",
    "fig.hub_type.alt": "October 2026: domain shares within top-level policy source types",
    "fig.korea.alt": "October 2026: policy sources citing Korean research and countries cited by Korean policy documents",
    "fig.two_speed.alt": "October 2026: citations per cited work and 2023–2025 work shares for the top 300 topics",
    "story.hub_country.kicker": "Policy Sources: Citation Totals and Averages",
    "story.hub_country.title": "Policy sources differ in citation totals and averages.",
    "story.hub_country.body":
      "Citation totals and average citations per citing policy document measure different quantities. Both panels show the same ten sources ranked by total citations.",
    "story.hub_type.kicker": "Policy Sources · Types",
    "story.hub_type.title": "Research domains differ by policy source type.",
    "story.hub_type.body":
      "The figure compares research domains within each policy source type. Each assigned domain is counted once per policy document–work citation. A citation to a work with several domains contributes to each domain.",
    "story.korea.kicker": "Korea",
    "story.korea.title": "Korea's two citation directions differ by country and field.",
    "story.korea.body":
      "Social sciences account for 64.2% of domain assignments in research cited by Korean policy documents and 23.1% in Korean research cited by policy documents. Country and field profiles describe different aspects of each direction.",
    "story.two_speed.kicker": "Citations per Cited Work and Share of Recent Works",
    "story.two_speed.title": "Topics differ in citation frequency and the share of recent works.",
    "story.two_speed.body":
      "The figure compares the top 300 topics by citation count. The recent-work share is the percentage published in 2023–2025 among cited works with a known publication year through 2025.",
    "monitor.kicker": "Key Metrics",
    "monitor.title": "Four key metrics for Korea's policy–research citations",
    "monitor.lede": "Read the two citation directions alongside the composition of policy sources and the frequency with which works appear in different policy documents.",
    "monitor.card1.value": "Social-science share gap: 41.1 pp",
    "monitor.card1.title": "Field-composition difference between directions",
    "monitor.card1.body": "Social sciences account for 64.2% of domain assignments in research cited by Korean policy documents and 23.1% in Korean research cited by policy documents.",
    "monitor.card2.value": "Top three policy sources: 49.7%",
    "monitor.card2.title": "Policy sources citing Korean research",
    "monitor.card2.body": "Combined share of the three largest policy source categories among citations to Korean research, counted by source category.",
    "monitor.card3.value": "Observed 45.4% · expected 35.1%",
    "monitor.card3.title": "Research cited by Korean policy documents",
    "monitor.card3.body": "Both shares use citations from Korean policy documents with a country and domain assigned. For the expected share, each citation contributes a total weight of one across its domains. The reference describes the linked sample, not total OpenAlex research output.",
    "monitor.card4.value": "KDI + KIEP: 5.2%",
    "monitor.card4.title": "Institutional composition of the Korean policy-document sample",
    "monitor.card4.body": "Combined share of citations from Korean policy documents published by these two institutions. Coverage differs across institutions.",
    "monitor.cta.next": "Explore the Latest Results and Data",
    "monitor.cta.next.href": "./SI/update_202603_en.html",
    "monitor.cta.report": "Open 2025 Baseline PDF",
    "explore.title": "Use this summary",
    "explore.lede": "Start with the English pages for a short web summary. The report manuscript and detailed SI are provided in Korean.",
    "explore.card.report.meta": "2025 baseline · Korean",
    "explore.card.report.title": "2025 Korean Report PDF",
    "explore.card.report.desc": "The 2025 analysis and figures in the manuscript prepared before publication editing",
    "explore.card.si.meta": "2025 baseline · issue 68 corrections",
    "explore.card.si.title": "2025 Baseline Summary",
    "explore.card.si.desc": "The 2025 findings with editorial corrections and links to the approved chapters",
    "explore.card.si.href": "./SI/index_en.html",
    "explore.card.update.meta": "Overton 2026-10-04 · OpenAlex 2026-06-25",
    "explore.card.update.title": "2026 Update Summary",
    "explore.card.update.desc": "Recomputed results, figures, aggregates and linkage checks",
    "explore.card.update.href": "./SI/update_202603_en.html",
    "explore.card.methods.meta": "Scope and denominators",
    "explore.card.methods.title": "Methods Summary",
    "explore.card.methods.desc": "Scope, denominators, and interpretation boundaries",
    "explore.card.methods.href": "./SI/methods_en.html",
    "explore.card.interactive.meta": "Selected figure comparisons",
    "explore.card.interactive.title": "Selected Figures",
    "explore.card.interactive.desc": "Interactive country, source-type and topic figures for the 2025 baseline",
    "explore.card.interactive.href": "./SI/interactive_en.html",
    "explore.card.appendix.meta": "Key definitions",
    "explore.card.appendix.title": "Definitions Summary",
    "explore.card.appendix.desc": "Compact definitions for key indicators",
    "explore.card.appendix.href": "./SI/appendix_en.html",
    "footer.title": "Korea's Two Policy-Research Citation Directions",
    "footer.link.top": "Back to top",
    "footer.link.report": "Korean Report Manuscript (PDF)",
    "footer.link.si": "English Summary",
    "footer.link.si.href": "./SI/index_en.html",
  };
  const koMeta = {
    title: document.title,
    description: document.querySelector('meta[name="description"]')?.getAttribute("content") || "",
  };

  function captureBaseline() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const record = baseline.get(el) || { attrs: {} };
      if (record.text == null) record.text = el.textContent;
      baseline.set(el, record);
    });

    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const record = baseline.get(el) || { attrs: {} };
      if (record.html == null) record.html = el.innerHTML;
      baseline.set(el, record);
    });

    document.querySelectorAll("[data-i18n-attr]").forEach((el) => {
      const record = baseline.get(el) || { attrs: {} };
      const raw = el.dataset.i18nAttr || "";
      raw
        .split(",")
        .map((p) => p.trim())
        .filter(Boolean)
        .forEach((pair) => {
          const [attr, _key] = pair.split(":").map((s) => s.trim());
          if (!attr) return;
          if (record.attrs[attr] == null) record.attrs[attr] = el.getAttribute(attr);
        });
      baseline.set(el, record);
    });
  }

  function applyLanguage(lang) {
    const safeLang = SUPPORTED_LANGS.includes(lang) ? lang : "ko";
    const dict = safeLang === "en" ? en : null;

    document.documentElement.lang = safeLang;
    document.documentElement.setAttribute("xml:lang", safeLang);
    document.documentElement.dataset.lang = safeLang;
    document.title = safeLang === "en" ? en["meta.title"] : koMeta.title;

    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute(
        "content",
        safeLang === "en" ? en["meta.description"] : koMeta.description
      );
    }

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const record = baseline.get(el);
      if (safeLang === "en") {
        const key = el.dataset.i18n;
        const next = dict && key ? dict[key] : null;
        if (next != null) el.textContent = next;
        else if (record && record.text != null) el.textContent = record.text;
      } else if (record && record.text != null) {
        el.textContent = record.text;
      }
    });

    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const record = baseline.get(el);
      if (safeLang === "en") {
        const key = el.dataset.i18nHtml;
        const next = dict && key ? dict[key] : null;
        if (next != null) el.innerHTML = next;
        else if (record && record.html != null) el.innerHTML = record.html;
      } else if (record && record.html != null) {
        el.innerHTML = record.html;
      }
    });

    document.querySelectorAll("[data-i18n-attr]").forEach((el) => {
      const record = baseline.get(el);
      const raw = el.dataset.i18nAttr || "";
      raw
        .split(",")
        .map((p) => p.trim())
        .filter(Boolean)
        .forEach((pair) => {
          const [attr, key] = pair.split(":").map((s) => s.trim());
          if (!attr || !key) return;
          if (safeLang === "en") {
            const next = dict && key ? dict[key] : null;
            if (next != null) el.setAttribute(attr, next);
            else if (record && record.attrs && record.attrs[attr] != null) el.setAttribute(attr, record.attrs[attr]);
          } else if (record && record.attrs && record.attrs[attr] != null) {
            el.setAttribute(attr, record.attrs[attr]);
          }
        });
    });

    window.dispatchEvent(new Event("resize"));
  }

  function initLanguage() {
    const switchEl = document.querySelector(".promo-lang-switch");
    if (!switchEl) return;
    if (switchEl.dataset.staticLangSwitch === "true") return;

    captureBaseline();

    const params = new URLSearchParams(window.location.search);
    const paramLang = (params.get("lang") || "").toLowerCase();
    const saved = (() => {
      try {
        return window.localStorage.getItem(LANG_STORAGE_KEY);
      } catch (_err) {
        return null;
      }
    })();

    const browserLang = (navigator.language || "").toLowerCase();
    const initial =
      (paramLang && SUPPORTED_LANGS.includes(paramLang) && paramLang) ||
      (saved && SUPPORTED_LANGS.includes(saved) && saved) ||
      (browserLang.startsWith("en") ? "en" : "ko");

    function setButtons(active) {
      switchEl.querySelectorAll("[data-lang]").forEach((btn) => {
        const isActive = btn.dataset.lang === active;
        btn.classList.toggle("is-active", isActive);
        btn.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
    }

    function setLanguage(next) {
      const safe = SUPPORTED_LANGS.includes(next) ? next : "ko";
      setButtons(safe);
      applyLanguage(safe);
      try {
        window.localStorage.setItem(LANG_STORAGE_KEY, safe);
      } catch (_err) {
        // ignore
      }
    }

    switchEl.addEventListener("click", (event) => {
      const btn = event.target.closest("[data-lang]");
      if (!btn) return;
      event.preventDefault();
      if (btn.dataset.lang === "en") {
        try {
          window.localStorage.setItem(LANG_STORAGE_KEY, "en");
        } catch (_err) {
          // ignore
        }
        window.location.href = "./index_en.html";
        return;
      }
      setLanguage(btn.dataset.lang);
    });

    setLanguage(initial);
  }

  function initReveal() {
    const targets = Array.from(document.querySelectorAll("[data-reveal]"));
    if (targets.length === 0) return;

    document.documentElement.classList.add("has-js");

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      targets.forEach((el) => el.classList.add("is-inview"));
      return;
    }

    targets.forEach((el) => {
      const rawDelay = el.dataset.revealDelay;
      if (!rawDelay) return;
      const delayMs = Number.parseInt(rawDelay, 10);
      if (Number.isFinite(delayMs) && delayMs > 0) {
        el.style.setProperty("--reveal-delay", `${delayMs}ms`);
      }
    });

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) entry.target.classList.add("is-inview");
          else entry.target.classList.remove("is-inview");
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );

    const viewportH = window.innerHeight || 1;
    targets.forEach((el) => {
      const rect = el.getBoundingClientRect();
      if (rect.top < viewportH * 0.85 && rect.bottom > 0) {
        el.classList.add("is-inview");
      }
      observer.observe(el);
    });
  }

  function initHeroParallax() {
    if (prefersReducedMotion) return;

    const hero = document.querySelector(".promo-hero");
    if (!hero) return;

    const visual = hero.querySelector(".promo-hero__visual");
    if (!visual) return;

    const globalBg = document.querySelector(".promo-bg");
    const bridge = document.querySelector(".promo-bridge");

    let ticking = false;

    function update() {
      ticking = false;

      if (globalBg) {
        const globalY = -window.scrollY * 0.03;
        globalBg.style.setProperty("--promo-bg-y", `${globalY.toFixed(2)}px`);
      }

      const rect = hero.getBoundingClientRect();
      const height = rect.height || 1;
      const raw = -rect.top / height;
      const progress = Math.min(1, Math.max(0, raw));

      const translateY = progress * 44;
      const scale = 1.08 + progress * 0.05;
      const opacity = 0.24 - progress * 0.14;
      const gridY = -progress * 26;

      visual.style.setProperty("--promo-hero-visual-y", `${translateY.toFixed(2)}px`);
      visual.style.setProperty("--promo-hero-visual-scale", scale.toFixed(3));
      visual.style.setProperty("--promo-hero-visual-opacity", opacity.toFixed(3));
      hero.style.setProperty("--promo-hero-grid-y", `${gridY.toFixed(2)}px`);

      if (bridge) {
        const rectB = bridge.getBoundingClientRect();
        const viewportH = window.innerHeight || 1;
        const rawB = (viewportH - rectB.top) / (viewportH || 1);
        const progressB = Math.min(1, Math.max(0, rawB));
        const easedB = 1 - Math.pow(1 - progressB, 3);
        const translateBridgeY = (1 - easedB) * 18;
        bridge.style.setProperty("--promo-bridge-visual-y", `${translateBridgeY.toFixed(2)}px`);
        const bridgeVisualOpacity = 0.84 + easedB * 0.16;
        const bridgeOverlayOpacity = Math.max(0, 0.16 * (1 - easedB));
        bridge.style.setProperty("--promo-bridge-visual-opacity", bridgeVisualOpacity.toFixed(3));
        bridge.style.setProperty("--promo-bridge-overlay-opacity", bridgeOverlayOpacity.toFixed(3));
      }
    }

    function requestUpdate() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }

    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate);
    requestUpdate();
  }

  function initScrolly(sectionEl) {
    const steps = Array.from(sectionEl.querySelectorAll(".promo-step[data-figure]"));
    const figures = Array.from(sectionEl.querySelectorAll(".promo-figure[data-figure-id]"));
    const sticky = sectionEl.querySelector(".promo-scrolly__sticky");
    const stage = sectionEl.querySelector(".promo-scrolly__stage");
    const progressCount = sectionEl.querySelector("[data-progress-count]");
    const progressFill = sectionEl.querySelector("[data-progress-fill]");

    if (steps.length === 0 || figures.length === 0) return;

    const figureById = new Map(figures.map((el) => [el.dataset.figureId, el]));
    const stepById = new Map(steps.map((el) => [el.dataset.figure, el]));

    let activeId = null;
    let ticking = false;

    function setActive(nextId) {
      if (!nextId || nextId === activeId) return;

      const prevStep = stepById.get(activeId);
      const prevFigure = figureById.get(activeId);
      if (prevStep) {
        prevStep.classList.remove("is-active");
        prevStep.removeAttribute("aria-current");
      }
      if (prevFigure) {
        prevFigure.classList.remove("is-active");
        prevFigure.setAttribute("aria-hidden", "true");
      }

      const nextStep = stepById.get(nextId);
      const nextFigure = figureById.get(nextId);
      if (nextStep) {
        nextStep.classList.add("is-active");
        nextStep.setAttribute("aria-current", "step");
      }
      if (nextFigure) {
        nextFigure.classList.add("is-active");
        nextFigure.setAttribute("aria-hidden", "false");
      }

      const nextIndex = steps.findIndex((step) => step.dataset.figure === nextId);
      if (stage) stage.dataset.scene = nextId;
      if (sticky) sticky.dataset.scene = nextId;
      if (progressCount && nextIndex >= 0) progressCount.textContent = `${nextIndex + 1} / ${steps.length}`;
      if (progressFill && nextIndex >= 0) {
        const ratio = steps.length > 0 ? (nextIndex + 1) / steps.length : 1;
        progressFill.style.width = `${Math.max(0, Math.min(1, ratio)) * 100}%`;
      }

      activeId = nextId;
    }

    function recalcActive() {
      ticking = false;

      const viewportH = window.innerHeight || 1;
      let focusY = viewportH * 0.62;
      let range = viewportH * 0.68;

      if (sticky) {
        const stickyRect = sticky.getBoundingClientRect();
        const stickyBottom = Math.min(viewportH, Math.max(0, stickyRect.bottom));
        const available = viewportH - stickyBottom;
        if (available >= 120) {
          focusY = stickyBottom + available * 0.55;
          range = Math.max(220, available * 1.35);
        }
      }
      let candidate = steps[0];
      let bestDist = Number.POSITIVE_INFINITY;
      let focusStep = null;

      for (const step of steps) {
        const rect = step.getBoundingClientRect();
        const center = rect.top + rect.height / 2;
        const dist = Math.abs(center - focusY);
        const containsFocus = rect.top <= focusY && rect.bottom >= focusY;
        if (containsFocus) focusStep = step;
        if (dist < bestDist) {
          bestDist = dist;
          candidate = step;
        }

        if (!prefersReducedMotion) {
          const normalized = Math.min(1, dist / (range || 1));
          const eased = Math.pow(1 - normalized, 2);
          const opacity = 0.12 + eased * 0.88;
          const signed = Math.max(-1, Math.min(1, (center - focusY) / (range || 1)));
          const translate = signed * 12;
          step.style.opacity = opacity.toFixed(3);
          step.style.transform = `translateY(${translate.toFixed(2)}px)`;
        }
      }

      if (focusStep) candidate = focusStep;
      setActive(candidate.dataset.figure);

      if (!prefersReducedMotion && candidate) {
        candidate.style.opacity = "1";
        candidate.style.transform = "translateY(-2px)";
      }
    }

    function requestRecalc() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(recalcActive);
    }

    // Initialize from any pre-set state in markup.
    const preset = steps.find((s) => s.classList.contains("is-active"));
    if (preset) setActive(preset.dataset.figure);
    else setActive(steps[0].dataset.figure);

    window.addEventListener("scroll", requestRecalc, { passive: true });
    window.addEventListener("resize", requestRecalc);
    requestRecalc();
  }

  function initOutroHideSticky() {
    const explore = document.querySelector(".promo-explore");
    const sticky = document.querySelector(".promo-scrolly__sticky");

    if (!explore || !sticky) return;
    if (!("IntersectionObserver" in window)) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) sticky.classList.add("is-hidden");
          else sticky.classList.remove("is-hidden");
        }
      },
      { threshold: 0.12, rootMargin: "-15% 0px -35% 0px" }
    );

    observer.observe(explore);
  }

  window.addEventListener("DOMContentLoaded", function () {
    initLanguage();
    initReveal();
    initHeroParallax();
    document.querySelectorAll("[data-scrolly]").forEach(initScrolly);
    initOutroHideSticky();
  });

  function resetScrollToTop() {
    const root = document.documentElement;
    const previousBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";
    window.scrollTo(0, 0);
    root.style.scrollBehavior = previousBehavior;

    if (window.location.hash) {
      try {
        window.history.replaceState(null, "", window.location.pathname + window.location.search);
      } catch (_err) {
        // Ignore; hash clearing is best-effort.
      }
    }
  }

  window.addEventListener("load", function () {
    resetScrollToTop();
  });

  window.addEventListener("pageshow", function (event) {
    if (event.persisted) resetScrollToTop();
  });
})();
