(function () {
  "use strict";

  const LANG_KEYS = ["promo_lang", "si_lang"];
  const SUPPORTED_LANGS = ["ko", "en"];
  const SI_PAGE_PAIRS = {
    "index.html": { ko: "index.html", en: "index_en.html" },
    "index_en.html": { ko: "index.html", en: "index_en.html" },
    "update_202603.html": { ko: "update_202603.html", en: "update_202603_en.html" },
    "update_202603_en.html": { ko: "update_202603.html", en: "update_202603_en.html" },
    "methods.html": { ko: "methods.html", en: "methods_en.html" },
    "methods_en.html": { ko: "methods.html", en: "methods_en.html" },
    "interactive.html": { ko: "interactive.html", en: "interactive_en.html" },
    "interactive_en.html": { ko: "interactive.html", en: "interactive_en.html" },
    "appendix.html": { ko: "appendix.html", en: "appendix_en.html" },
    "appendix_en.html": { ko: "appendix.html", en: "appendix_en.html" },
    "next_questions.html": { ko: "next_questions.html", en: "next_questions_en.html" },
    "next_questions_en.html": { ko: "next_questions.html", en: "next_questions_en.html" },
  };
  const NAV_ITEMS = {
    ko: {
      main: { text: "메인", href: "../index.html" },
      report: { text: "보고서(PDF)", href: "../Report/Report_final.pdf" },
      menu: "확장 자료",
      items: [
        { text: "확장 자료", href: "../SI/index.html" },
        { text: "2026 데이터 업데이트", href: "../SI/update_202603.html" },
        { text: "방법론·데이터 정합성", href: "../SI/methods.html" },
        { text: "인터랙티브", href: "../SI/interactive.html" },
        { text: "부록", href: "../SI/appendix.html" },
        { text: "다음 질문", href: "../SI/next_questions.html" },
      ],
    },
    en: {
      main: { text: "Main", href: "../index_en.html" },
      report: { text: "Korean Report (PDF)", href: "../Report/Report_final.pdf" },
      menu: "English Summary",
      items: [
        { text: "English Summary", href: "../SI/index_en.html" },
        { text: "2026 Update Summary", href: "../SI/update_202603_en.html" },
        { text: "Methods Summary", href: "../SI/methods_en.html" },
        { text: "Selected Figures", href: "../SI/interactive_en.html" },
        { text: "Definitions Summary", href: "../SI/appendix_en.html" },
        { text: "Next Questions Summary", href: "../SI/next_questions_en.html" },
      ],
    },
  };

  function getFileName() {
    try {
      const url = new URL(window.location.href);
      const parts = url.pathname.split("/").filter(Boolean);
      return parts.length ? parts[parts.length - 1] : "";
    } catch (_err) {
      return "";
    }
  }

  function isSIPage(fileName) {
    if (!isInSIDir()) return false;
    return Boolean(SI_PAGE_PAIRS[fileName]);
  }

  function isInSIDir() {
    try {
      const url = new URL(window.location.href);
      return url.pathname.split("/").includes("SI");
    } catch (_err) {
      return false;
    }
  }

  function getPreferredLang(fileName) {
    let paramLang = null;
    try {
      const url = new URL(window.location.href);
      paramLang = (url.searchParams.get("lang") || "").toLowerCase();
    } catch (_err) {
      // ignore
    }
    if (SUPPORTED_LANGS.includes(paramLang)) return paramLang;

    // Explicit page variants win. This keeps direct links stable:
    // *_en.html opens English, while the base .html pages remain Korean.
    if (typeof fileName === "string" && fileName.endsWith("_en.html")) return "en";
    if (isSIPage(fileName)) return "ko";

    for (const k of LANG_KEYS) {
      try {
        const saved = window.localStorage.getItem(k);
        if (SUPPORTED_LANGS.includes(saved)) return saved;
      } catch (_err) {
        // ignore
      }
    }

    const browserLang = (navigator.language || "").toLowerCase();
    return browserLang.startsWith("en") ? "en" : "ko";
  }

  function setPreferredLang(lang) {
    const safe = SUPPORTED_LANGS.includes(lang) ? lang : "ko";
    for (const k of LANG_KEYS) {
      try {
        window.localStorage.setItem(k, safe);
      } catch (_err) {
        // ignore
      }
    }
  }

  function withLangParam(rawHref, lang) {
    if (!rawHref) return rawHref;
    try {
      const url = new URL(rawHref, window.location.href);
      if (lang === "en") url.searchParams.set("lang", "en");
      else url.searchParams.set("lang", "ko");
      return url.toString();
    } catch (_err) {
      // Fallback: best-effort append.
      const sep = rawHref.includes("?") ? "&" : "?";
      return `${rawHref}${sep}lang=${encodeURIComponent(lang)}`;
    }
  }

  function setUrlLangParam(lang) {
    try {
      const url = new URL(window.location.href);
      url.searchParams.set("lang", lang);
      window.history.replaceState({}, "", url.toString());
    } catch (_err) {
      // ignore
    }
  }

  function getLanguagePageUrl(fileName, lang) {
    const pair = SI_PAGE_PAIRS[fileName];
    const targetFileName = pair ? pair[lang] : null;
    if (!targetFileName || targetFileName === fileName) return null;

    try {
      const url = new URL(window.location.href);
      const parts = url.pathname.split("/");
      parts[parts.length - 1] = targetFileName;
      url.pathname = parts.join("/");
      url.searchParams.delete("lang");
      return url.toString();
    } catch (_err) {
      return targetFileName;
    }
  }

  function navigateToLanguagePage(fileName, lang, mode) {
    const targetUrl = getLanguagePageUrl(fileName, lang);
    if (!targetUrl) return false;
    if (mode === "replace") window.location.replace(targetUrl);
    else window.location.href = targetUrl;
    return true;
  }

  function mountIframe(container) {
    if (!container || container.querySelector("iframe")) return;
    const src = container.getAttribute("data-src");
    const height = container.getAttribute("data-height") || "650";
    const title = container.getAttribute("data-title") || "Interactive plot";
    if (!src) return;

    const iframe = document.createElement("iframe");
    iframe.src = src;
    iframe.height = height;
    iframe.loading = "lazy";
    iframe.setAttribute("title", title);
    container.appendChild(iframe);
  }

  function initPlotLoaders() {
    document.querySelectorAll(".si-plot").forEach((container) => {
      const btn = container.querySelector(".si-plot__btn");
      if (!btn) return;
      btn.addEventListener("click", () => {
        mountIframe(container);
        btn.remove();
      });
    });
  }

  function openDetailsForHash() {
    if (!window.location.hash) return;
    const id = window.location.hash.slice(1);
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;

    let details = target.closest("details");
    while (details) {
      details.open = true;
      details = details.parentElement ? details.parentElement.closest("details") : null;
    }
  }

  function autoloadPlotForHash() {
    if (!window.location.hash) return;
    const selector = window.location.hash;
    let target = null;
    try {
      target = document.querySelector(selector);
    } catch (_err) {
      return;
    }
    if (!target) return;

    const container = target.querySelector ? target.querySelector(".si-plot") : null;
    if (!container) return;

    const btn = container.querySelector(".si-plot__btn");
    mountIframe(container);
    if (btn) btn.remove();
  }

  function updatePlotLinksAndFrames(lang) {
    const safe = SUPPORTED_LANGS.includes(lang) ? lang : "ko";
    const targetOrigin = window.location.origin === "null" ? "*" : window.location.origin;

    document.querySelectorAll(".si-plot").forEach((container) => {
      const rawSrc = container.dataset.srcBase || container.getAttribute("data-src") || "";
      if (!container.dataset.srcBase && rawSrc) container.dataset.srcBase = rawSrc;

      if (rawSrc) container.setAttribute("data-src", withLangParam(rawSrc, safe));

      const link = container.querySelector("a.si-plot__link");
      if (link) {
        const rawHref = link.dataset.hrefBase || link.getAttribute("href") || "";
        if (!link.dataset.hrefBase && rawHref) link.dataset.hrefBase = rawHref;
        if (rawHref) link.setAttribute("href", withLangParam(rawHref, safe));
      }

      const iframe = container.querySelector("iframe");
      if (iframe && iframe.contentWindow) {
        try {
          iframe.contentWindow.postMessage({ type: "si:setLang", lang: safe }, targetOrigin);
        } catch (_err) {
          // ignore
        }
      }
    });
  }

  function updateNavbar(lang) {
    const nav = NAV_ITEMS[SUPPORTED_LANGS.includes(lang) ? lang : "ko"];
    const topLinks = Array.from(document.querySelectorAll(".navbar-nav > .nav-item > .nav-link"));

    function setLink(link, item, textSelector) {
      if (!link || !item) return;
      link.setAttribute("href", item.href);
      const textEl = link.querySelector(textSelector || ".menu-text");
      if (textEl) textEl.textContent = item.text;
    }

    setLink(topLinks[0], nav.main);
    setLink(topLinks[1], nav.report);

    const dropdownToggle = document.querySelector(".navbar-nav .dropdown-toggle .menu-text");
    if (dropdownToggle) dropdownToggle.textContent = nav.menu;

    const dropdownItems = Array.from(document.querySelectorAll(".navbar-nav .dropdown-menu .dropdown-item"));
    nav.items.forEach((item, index) => {
      setLink(dropdownItems[index], item, ".dropdown-text");
    });
  }

  function updateSearchVisibility(lang) {
    const search = document.getElementById("quarto-search");
    if (!search) return;
    search.hidden = false;
    search.setAttribute("aria-hidden", "false");
  }

  function applyLanguage(lang) {
    const safe = SUPPORTED_LANGS.includes(lang) ? lang : "ko";
    document.documentElement.dataset.siLang = safe;
    updateNavbar(safe);
    updateSearchVisibility(safe);
    updatePlotLinksAndFrames(safe);
  }

  function insertLanguageSwitch(fileName) {
    if (!isSIPage(fileName)) return;

    const wrapper = document.createElement("div");
    wrapper.className = "si-lang-switch";
    wrapper.setAttribute("role", "group");
    wrapper.setAttribute("aria-label", "Language");

    const korBtn = document.createElement("button");
    korBtn.type = "button";
    korBtn.className = "si-lang-btn";
    korBtn.dataset.lang = "ko";
    korBtn.textContent = "KOR";

    const enBtn = document.createElement("button");
    enBtn.type = "button";
    enBtn.className = "si-lang-btn";
    enBtn.dataset.lang = "en";
    enBtn.textContent = "ENG";

    function setButtons(active) {
      [korBtn, enBtn].forEach((btn) => {
        const isActive = btn.dataset.lang === active;
        btn.classList.toggle("is-active", isActive);
        btn.setAttribute("aria-pressed", isActive ? "true" : "false");
      });
    }

    function go(next) {
      const safe = SUPPORTED_LANGS.includes(next) ? next : "ko";
      setPreferredLang(safe);
      if (navigateToLanguagePage(fileName, safe, "assign")) return;
      setUrlLangParam(safe);
      setButtons(safe);
      applyLanguage(safe);
    }

    wrapper.addEventListener("click", (event) => {
      const btn = event.target.closest("button[data-lang]");
      if (!btn) return;
      event.preventDefault();
      go(btn.dataset.lang);
    });

    wrapper.appendChild(korBtn);
    wrapper.appendChild(enBtn);

    const navbarTools = document.querySelector(".quarto-navbar-tools");
    if (navbarTools) {
      navbarTools.appendChild(wrapper);
    } else {
      wrapper.classList.add("si-lang-switch--floating");
      document.body.appendChild(wrapper);
    }

    // initial state
    const initial = getPreferredLang(fileName);
    setButtons(initial);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const fileName = getFileName();
    if (!isSIPage(fileName)) return;

    const initialLang = getPreferredLang(fileName);
    setPreferredLang(initialLang);
    if (navigateToLanguagePage(fileName, initialLang, "replace")) return;
    applyLanguage(initialLang);

    initPlotLoaders();
    openDetailsForHash();
    autoloadPlotForHash();

    window.addEventListener("hashchange", () => {
      openDetailsForHash();
      autoloadPlotForHash();
    });

    insertLanguageSwitch(fileName);
  });
})();
