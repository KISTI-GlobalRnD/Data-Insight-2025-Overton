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
    "meta.title": "Overton × OpenAlex — Data Insight",
    "meta.description":
      "A one-page view of when, what, and where policy draws scientific evidence by combining Overton policy citations with OpenAlex metadata.",
    "skip.link": "Skip to content",
    "lang.aria": "Language",
    "hero.kicker": "2025 DATA INSIGHT",
    "hero.brand": "KISTI Center for Global R&D Analysis",
    "hero.title": "Science flows into policy — but the paths are not even.",
    "hero.lede":
      "Most policy documents cite scholarly research. Which domains and topics are repeatedly called upon, and which countries and institutions sit at the center of the flow?",
    "hero.lede2":
      "By combining Overton citation logs with OpenAlex metadata, we summarize in one page <strong>when, what, and where</strong> policy pulls evidence from science.",
    "hero.actions.aria": "Quick links",
    "hero.cta.summary": "View key summary",
    "hero.cta.si": "Go to Supplementary Information",
    "bridge.aria": "Key message",
    "bridge.eyebrow": "Why this map matters",
    "bridge.title": "How evidence flows can matter more than how much.",
    "bridge.body":
      "Policy citations are not just totals—they are connections (routes). Seeing which studies are repeatedly called through which channels, and which countries, institutions, and topics become hubs, reveals the structure of the policy–science linkage.",
    "bridge.body2":
      "This page walks through <strong>when, what, and where</strong> policy draws evidence, based on DOI-linked citations.",
    "bridge.chips.aria": "Reading order",
    "bridge.chip.when": "When: growth and citation density",
    "bridge.chip.what": "What: skew across domains and topics",
    "bridge.chip.where": "Where: hubs across countries and institutions",
    "bridge.actions.aria": "Next",
    "bridge.cta.summary": "See overview metrics",
    "bridge.cta.story": "Jump to scrolly story",
    "intro.title": "At a glance",
    "intro.lede":
      "Start with overall scale and coverage, based on DOI-linked policy→research citations. Definitions, constraints, and metric notes are in the Supplementary Information.",
    "intro.stats.aria": "Summary metrics",
    "intro.stat.links": "Policy → research citation links",
    "intro.stat.links.value": "23.37M",
    "intro.stat.docs": "Policy documents (deduplicated)",
    "intro.stat.docs.value": "1.38M",
    "intro.stat.dois": "Distinct cited DOIs",
    "intro.stat.dois.value": "6.53M",
    "intro.stat.coverage": "Policy docs with citations",
    "intro.stat.coverage.value": "97.6%",
    "intro.meta.snapshot": "Data snapshot: Overton 2025.02 · OpenAlex 2025.06 · DOI-based matching",
    "intro.meta.link": "Scroll the story",
    "fig.korea.alt": "Korea policy–research flows in two directions (inbound/sourcing; top 10)",
    "fig.network.alt":
      "Policy–research evidence flow network (top 50 nodes; top-3 inbound/outbound links per node)",
    "fig.hub.alt": "Policy citations by policy source country (top 10 + Korea)",
    "fig.domain.alt": "Policy citations by domain (top 10)",
    "fig.topics.alt": "Topics: citation intensity vs recency",
    "fig.pubyear.alt": "Policy citations, document counts, and average citations per document by publication year",
    "story.steps.aria": "Story steps",
    "story.korea.kicker": "1 · Mirror",
    "story.korea.title": "Korea: inbound and sourcing paths diverge",
    "story.korea.body":
      "From Korea’s perspective, the path through which Korean research is cited in global policy (inbound) and the path through which Korean policy pulls evidence (sourcing) do not move in the same way. Inbound citations are often observed via hub routes such as the UK, international organizations, and the US, while sourcing shows stronger dependence on specific channels (e.g., a higher US share).",
    "story.network.kicker": "2 · Map",
    "story.network.title": "Evidence spreads via transfers, not direct flights",
    "story.network.body":
      "We focus on the top 50 policy sources and research countries, keeping only each node’s top-3 inbound and top-3 outbound links to reveal the backbone of the flow. Connections concentrate around a few hubs, making it easier to see which hubs Korea is tied to.",
    "story.hub.kicker": "3 · Hubs",
    "story.hub.title": "Policy evidence accumulates in a few sources",
    "story.hub.body":
      "Total policy citations are highly concentrated in a small set of sources—IGOs, the United States, the United Kingdom, and the EU. This anchors the “hub” pattern as a quantitative fact, not just a visual impression.",
    "story.domain.kicker": "4 · Skew",
    "story.domain.title": "High volume doesn’t mean citing all science",
    "story.domain.body":
      "At the domain level, policy citations are heavily skewed toward a few fields. So “policy uses a lot of science” doesn’t automatically mean it draws on a wide range of science; it shows where policy documents most often require evidence.",
    "story.topics.kicker": "5 · Pace",
    "story.topics.title": "Mature and fast-rising agendas move differently",
    "story.topics.body":
      "Plotting topics by citation intensity (policy citations per paper) and recency (share in the last three years) separates mature topics that are steadily cited from high-growth topics that surge quickly. Shock-driven agendas like pandemics or climate can see both recency and intensity rise together, while infrastructural agendas tend to remain steadier.",
    "story.pubyear.kicker": "6 · Scale",
    "story.pubyear.title": "Policy citations keep rising",
    "story.pubyear.body":
      "Since the 2010s, DOI citations and the number of policy documents rose rapidly, peaking around 2021. Average citations per document can spike in specific years, but in the longer run it stays around ~18 on average. The most recent 4–5 years may appear lower because policy citations take time to accumulate after publication.",
    "explore.title": "Explore further",
    "explore.lede":
      "Continue with the full report (PDF), interactive versions of the figures, and the Supplementary Information.",
    "explore.actions.aria": "More",
    "explore.cta.report": "Open report PDF",
    "explore.cta.interactive": "Interactive figures",
    "explore.cta.si": "Open Supplementary Information",
    "footer.org": "<div class=\"promo-footer__org-primary\">KISTI Center for Global R&amp;D Analysis</div><div class=\"promo-footer__org-secondary\">KISTI 글로벌R&amp;D분석센터</div>",
    "footer.report.title": "From Science to Policy: Mapping Knowledge Diffusion through the OpenAlex–Overton Network",
    "footer.report.author":
      "Youngjin Kim · KISTI Center for Global R&amp;D Analysis · <a class=\"promo-footer__mailto\" href=\"mailto:kimyoungjin06@kisti.re.kr\">kimyoungjin06@kisti.re.kr</a>",
    "footer.character.alt": "KISTI Center for Global R&D Analysis character",
    "footer.nav.aria": "Footer links",
    "footer.link.top": "Back to top",
    "footer.link.report": "Report PDF",
    "footer.link.si": "Supplementary Information",
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
    document.documentElement.dataset.lang = safeLang;

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

    captureBaseline();

    const params = new URLSearchParams(window.location.search);
    const paramLang = params.get("lang");
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
