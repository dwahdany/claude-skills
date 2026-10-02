// Included by every template: render_html.py reads data-doc-height to size the screenshot.
// Measured after web fonts are ready, otherwise the fallback font's (shorter) layout is reported.
(function () {
  function measure() {
    var h = Math.ceil(document.documentElement.getBoundingClientRect().height);
    document.documentElement.setAttribute("data-doc-height", String(h));
  }
  function ready() { (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(measure, measure); }
  if (document.readyState === "complete") ready(); else window.addEventListener("load", ready);
  document.addEventListener("DOMContentLoaded", measure); // early value in case load never fires
})();
