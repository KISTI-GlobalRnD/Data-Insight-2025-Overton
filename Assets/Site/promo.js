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
    "meta.title": "Research Citations in Policy Documents | Overton × OpenAlex",
    "meta.description":
      "A concise web-only English summary of DOI-linked research citations in policy documents using Overton and OpenAlex.",
    "skip.link": "Skip to content",
    "lang.aria": "Language",
    "hero.kicker": "Analysis Results",
    "hero.title": "Research citations in policy documents are concentrated among a small number of policy sources.",
    "hero.lede":
      "The United States, international organizations, and the United Kingdom account for a combined 54.8% of the top policy sources citing Korean research. U.S.-authored research accounts for 55.7% of research citations from Korean policy documents. This page reports policy-source totals and per-document averages, field composition by source type, policy sources citing Korean research, research countries cited by Korean policy documents, and topic-level policy citations per paper and recent unique-paper shares.",
    "hero.lede2":
      "This page is a <strong>web-only English summary</strong>. The report manuscript and detailed SI are provided in Korean. It reports only DOI-linked policy-document → scholarly-article citations included in the current Overton data. The current PDF is a pre-editing manuscript; its link will be replaced when the final edited report is published.",
    "hero.actions.aria": "Quick links",
    "hero.cta.report": "Open Korean Report Manuscript (PDF)",
    "hero.cta.si": "Read English Summary",
    "hero.cta.si.href": "./SI/index_en.html",
    "hero.stats.aria": "Main numbers",
    "hero.stat.inbound": "Combined share of the top 3 policy sources citing Korean research",
    "hero.stat.sourcing": "Share of U.S. research in citations from Korean policy documents",
    "hero.stat.repeat": "Share of unique cited works cited at least twice",
    "hero.meta.snapshot": "Data snapshot: Overton 2025.02 · OpenAlex 2025.06 · DOI-linked citations",
    "hero.scroll": "Scroll",
    "story.kicker": "Main Comparisons",
    "story.title": "Four analysis results",
    "story.progress.label": "Item",
    "story.steps.aria": "Analysis items",
    "fig.hub_country.alt": "Policy-source citation totals, average citations per document, and domain composition",
    "fig.hub_type.alt": "Relationship between policy source type and research-domain composition",
    "fig.korea.alt": "Policy sources citing Korean research and research countries cited by Korean policy documents (top 10)",
    "fig.two_speed.alt": "Policy citations per paper and share of unique papers published in 2022-2024 by topic",
    "story.hub_country.kicker": "Policy Sources · Total and Per Document",
    "story.hub_country.title": "Rankings by total citations and average citations per document differ.",
    "story.hub_country.body":
      "Total citations are highest for international organizations, the United States, and the United Kingdom; average citations per document are 24.5 for Germany, 21.4 for international organizations, and 18.7 for France.",
    "story.hub_type.kicker": "Policy Sources · Types",
    "story.hub_type.title": "Research-field shares differ by policy source type.",
    "story.hub_type.body":
      "Development banks and think tanks cite more social-science research, while health agencies and aggregator-type services show larger health-science shares.",
    "story.korea.kicker": "Korea",
    "story.korea.title": "Policy sources citing Korean research and research countries cited by Korean policy documents have different distributions.",
    "story.korea.body":
      "The top 3 policy sources account for 54.8% of citations to Korean research, while U.S.-authored research accounts for 55.7% of research citations from Korean policy documents.",
    "story.two_speed.kicker": "Policy Citations per Paper and Recent Unique-Paper Share",
    "story.two_speed.title": "The two indicator values differ by topic.",
    "story.two_speed.body":
      "COVID-19-related topics have high recent unique-paper shares, while economics and labor topics have high policy citations per paper.",
    "monitor.kicker": "Monitoring",
    "monitor.title": "Four indicators to recalculate with the same definitions",
    "monitor.lede": "Recalculate the overall top-three policy-source share, the top-three policy-source share for citations to Korean research, the U.S.-research share in Korean policy documents, and the repeat-cited paper share with the same definitions.",
    "monitor.card1.value": "Policy-source rankings",
    "monitor.card1.title": "Total citations and average citations per document",
    "monitor.card1.body": "Compare the total-citation ranking with the average-citations-per-document ranking.",
    "monitor.card2.value": "Top 3 policy sources: 54.8%",
    "monitor.card2.title": "Policy sources citing Korean research",
    "monitor.card2.body": "Report the percentage-point difference between the combined U.S., IGO, and U.K. share and its baseline.",
    "monitor.card3.value": "Top research country: 55.7%",
    "monitor.card3.title": "Research cited by Korean policy documents",
    "monitor.card3.body": "Report the percentage-point difference between the U.S. research share and its baseline.",
    "monitor.card4.value": "Cited at least twice: 48.1%",
    "monitor.card4.title": "Share of papers cited at least twice",
    "monitor.card4.body": "Track the repeat-cited share and concentration among the most-cited works.",
    "monitor.cta.next": "Open Monitoring Questions",
    "monitor.cta.next.href": "./SI/next_questions_en.html",
    "monitor.cta.report": "Open Korean Report Manuscript (PDF)",
    "explore.title": "Use this summary",
    "explore.lede": "Start with the English pages for a short web summary. The report manuscript and detailed SI are provided in Korean.",
    "explore.card.report.meta": "Pre-editing manuscript · Korean",
    "explore.card.report.title": "Korean Report Manuscript (PDF)",
    "explore.card.report.desc": "Pre-editing Korean manuscript with the full analysis, figure captions, and interpretation",
    "explore.card.si.meta": "English web summary · 3 min",
    "explore.card.si.title": "English Summary",
    "explore.card.si.desc": "Concise overview of the report message, scope, definitions, and monitoring questions",
    "explore.card.si.href": "./SI/index_en.html",
    "explore.card.update.meta": "Web update",
    "explore.card.update.title": "2026 Update Summary",
    "explore.card.update.desc": "High-level comparison with the newer data",
    "explore.card.update.href": "./SI/update_202603_en.html",
    "explore.card.methods.meta": "Scope and denominators",
    "explore.card.methods.title": "Methods Summary",
    "explore.card.methods.desc": "Scope, denominators, and interpretation boundaries",
    "explore.card.methods.href": "./SI/methods_en.html",
    "explore.card.interactive.meta": "Selected figure comparisons",
    "explore.card.interactive.title": "Selected Figures",
    "explore.card.interactive.desc": "Short guide to selected interactive figures",
    "explore.card.interactive.href": "./SI/interactive_en.html",
    "explore.card.appendix.meta": "Key definitions",
    "explore.card.appendix.title": "Definitions Summary",
    "explore.card.appendix.desc": "Compact definitions for key indicators",
    "explore.card.appendix.href": "./SI/appendix_en.html",
    "footer.title": "Research Citations in Policy Documents",
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
