// GA4 for hongsgcpl.com, loaded ONLY after the visitor clicks Accept on the consent banner.
// The banner and the footer "Cookie settings" control are rendered hidden by build_pages.py;
// this file unhides them, and only on the live domain, so local previews never show a banner
// or count a visit. Before Accept: no gtag script element, no request to Google.
// No Consent Mode (it still sends pings). Choice: localStorage["pv_analytics_consent"] =
// "granted" | "denied". Storage failing reads as "no choice yet", so GA stays off.
(function () {
  var me = document.currentScript;
  var GA_ID = me && me.getAttribute("data-ga");
  if (!GA_ID || !/^(www\.)?hongsgcpl\.com$/.test(location.hostname)) return;

  var KEY = "pv_analytics_consent";
  var gaLoaded = false;
  var banner;

  function readChoice() {
    try {
      var v = window.localStorage.getItem(KEY);
      return v === "granted" || v === "denied" ? v : null;
    } catch (e) { return null; }
  }
  function writeChoice(v) {
    try { window.localStorage.setItem(KEY, v); } catch (e) { /* lasts this page view only */ }
  }
  function clearChoice() {
    try { window.localStorage.removeItem(KEY); } catch (e) { /* nothing stored */ }
  }

  function loadGA() {
    if (gaLoaded) return;
    gaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", GA_ID);
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
  }

  function pad() {
    // Keep the footer reachable: pad the page by the banner's height while it shows.
    document.body.style.paddingBottom = banner && !banner.hidden ? banner.offsetHeight + "px" : "";
  }

  function show(focus) {
    banner.hidden = false;
    pad();
    if (focus) {
      var b = banner.querySelector("button");
      if (b) b.focus();
    }
  }

  function hide() {
    var hadFocus = banner.contains(document.activeElement);
    banner.hidden = true;
    pad();
    if (hadFocus) {
      var s = document.querySelector("[data-consent-settings] button");
      if (s) s.focus();
    }
  }

  function choose(v) {
    writeChoice(v);
    hide();
    if (v === "granted") loadGA();
    else if (gaLoaded) location.reload(); // GA already ran this page view: reload so it is gone
  }

  function init() {
    banner = document.querySelector(".consent");
    if (!banner) return; // no banner markup: fail closed, load nothing
    banner.addEventListener("click", function (e) {
      var v = e.target && e.target.getAttribute && e.target.getAttribute("data-consent");
      if (v === "granted" || v === "denied") choose(v);
    });
    window.addEventListener("resize", pad);
    var links = document.querySelectorAll("[data-consent-settings]");
    for (var i = 0; i < links.length; i++) {
      links[i].hidden = false;
      var b = links[i].querySelector("button");
      if (b) b.addEventListener("click", function () { clearChoice(); show(true); });
    }
    var choice = readChoice();
    if (choice === "granted") loadGA();
    else if (choice === null) show(false);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
