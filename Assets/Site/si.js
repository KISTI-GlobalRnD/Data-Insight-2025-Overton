(function () {
  "use strict";

  const LANG_STORAGE_KEY = "si_lang";

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
    return (
      fileName === "index.html" ||
      fileName === "interactive.html" ||
      fileName === "appendix.html" ||
      fileName === "next_questions.html" ||
      fileName === "index_en.html" ||
      fileName === "interactive_en.html" ||
      fileName === "appendix_en.html" ||
      fileName === "next_questions_en.html"
    );
  }

  function computeLangUrls(fileName) {
    const isEn = fileName.endsWith("_en.html");
    const base = fileName.replace(/_en\.html$/, "").replace(/\.html$/, "");
    const korFile = `${base}.html`;
    const enFile = `${base}_en.html`;

    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);
    params.delete("lang");
    const search = params.toString() ? `?${params.toString()}` : "";
    const hash = url.hash || "";

    return {
      isEn,
      base,
      korHref: `${korFile}${search}${hash}`,
      enHref: `${enFile}${search}${hash}`,
    };
  }

  function getPreferredLang() {
    const url = new URL(window.location.href);
    const param = (url.searchParams.get("lang") || "").toLowerCase();
    if (param === "en" || param === "ko") return param;
    try {
      const saved = window.localStorage.getItem(LANG_STORAGE_KEY);
      if (saved === "en" || saved === "ko") return saved;
    } catch (_err) {
      // ignore
    }
    return "ko";
  }

  function setPreferredLang(lang) {
    try {
      window.localStorage.setItem(LANG_STORAGE_KEY, lang);
    } catch (_err) {
      // ignore
    }
  }

  function maybeRedirectForLang(fileName) {
    if (!isSIPage(fileName)) return;
    const pref = getPreferredLang();
    const { isEn, korHref, enHref } = computeLangUrls(fileName);
    if (pref === "en" && !isEn) window.location.replace(enHref);
    if (pref === "ko" && isEn) window.location.replace(korHref);
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

  function setLanguageSwitchInNavbarForEnglish() {
    const isEnglish = (document.documentElement.lang || "").toLowerCase().startsWith("en");
    if (!isEnglish) return;

    const mappings = [
      { selector: 'a.nav-link[href$="Report/Report_final_rev.pdf"] .menu-text', text: "Report (PDF, rev)" },
      { selector: "#nav-menu-si .menu-text", text: "Supplementary (SI)" },
      { selector: 'a.dropdown-item[href$="SI/index.html"] .dropdown-text', text: "Overview", hrefSuffix: "index_en.html" },
      {
        selector: 'a.dropdown-item[href$="SI/interactive.html"] .dropdown-text',
        text: "Interactive",
        hrefSuffix: "interactive_en.html",
      },
      { selector: 'a.dropdown-item[href$="SI/appendix.html"] .dropdown-text', text: "Appendix", hrefSuffix: "appendix_en.html" },
      {
        selector: 'a.dropdown-item[href$="SI/next_questions.html"] .dropdown-text',
        text: "Next questions",
        hrefSuffix: "next_questions_en.html",
      },
    ];

    mappings.forEach((m) => {
      const el = document.querySelector(m.selector);
      if (!el) return;
      el.textContent = m.text;

      if (!m.hrefSuffix) return;
      const link = el.closest("a");
      if (!link) return;
      const href = link.getAttribute("href");
      if (!href) return;
      const next = href.replace(/SI\/index\.html$/, `SI/${m.hrefSuffix}`)
        .replace(/SI\/interactive\.html$/, `SI/${m.hrefSuffix}`)
        .replace(/SI\/appendix\.html$/, `SI/${m.hrefSuffix}`)
        .replace(/SI\/next_questions\.html$/, `SI/${m.hrefSuffix}`);
      link.setAttribute("href", next);
    });
  }

  function insertLanguageSwitch(fileName) {
    if (!isSIPage(fileName)) return;

    const { isEn, korHref, enHref } = computeLangUrls(fileName);

    const wrapper = document.createElement("div");
    wrapper.className = "si-lang-switch";
    wrapper.setAttribute("role", "group");
    wrapper.setAttribute("aria-label", "Language");

    const korBtn = document.createElement("button");
    korBtn.type = "button";
    korBtn.className = `si-lang-btn${isEn ? "" : " is-active"}`;
    korBtn.dataset.lang = "ko";
    korBtn.setAttribute("aria-pressed", isEn ? "false" : "true");
    korBtn.textContent = "KOR";

    const enBtn = document.createElement("button");
    enBtn.type = "button";
    enBtn.className = `si-lang-btn${isEn ? " is-active" : ""}`;
    enBtn.dataset.lang = "en";
    enBtn.setAttribute("aria-pressed", isEn ? "true" : "false");
    enBtn.textContent = "ENG";

    function go(lang) {
      setPreferredLang(lang);
      window.location.href = lang === "en" ? enHref : korHref;
    }

    korBtn.addEventListener("click", () => go("ko"));
    enBtn.addEventListener("click", () => go("en"));

    wrapper.appendChild(korBtn);
    wrapper.appendChild(enBtn);

    const navbarTools = document.querySelector(".quarto-navbar-tools");
    if (navbarTools) {
      navbarTools.appendChild(wrapper);
      return;
    }

    wrapper.classList.add("si-lang-switch--floating");
    document.body.appendChild(wrapper);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const fileName = getFileName();
    maybeRedirectForLang(fileName);

    initPlotLoaders();
    openDetailsForHash();
    autoloadPlotForHash();

    window.addEventListener("hashchange", () => {
      openDetailsForHash();
      autoloadPlotForHash();
    });

    insertLanguageSwitch(fileName);
    setLanguageSwitchInNavbarForEnglish();
  });
})();

