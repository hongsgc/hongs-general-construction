// Estimate form: posts to Web3Forms with fetch, falls back to a normal POST without JS.
(function () {
  var form = document.getElementById("estimate");
  if (!form) return;
  var status = form.querySelector(".status");
  var button = form.querySelector("button[type=submit]");
  var t = form.dataset;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    status.className = "status";
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    button.disabled = true;
    status.textContent = t.sending;
    fetch(form.action, {
      method: "POST",
      headers: { Accept: "application/json" },
      body: new FormData(form),
    })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok && j.success, j: j }; }); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.j && res.j.message);
        form.reset();
        status.className = "status ok";
        status.textContent = t.ok;
      })
      .catch(function () {
        status.className = "status err";
        status.textContent = t.err;
      })
      .finally(function () { button.disabled = false; });
  });
})();

// Our work: category tabs + full-size photo viewer. Without JS, every photo shows and links to its full-size file.
(function () {
  var sec = document.getElementById("work");
  if (!sec) return;
  var tabs = sec.querySelector(".wtabs");
  var figs = [].slice.call(sec.querySelectorAll(".wgrid figure"));
  var lb = sec.querySelector(".lb");

  if (tabs) {
    tabs.hidden = false;
    tabs.addEventListener("click", function (ev) {
      var b = ev.target.closest("button");
      if (!b) return;
      var cat = b.dataset.cat;
      [].forEach.call(tabs.querySelectorAll("button"), function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      figs.forEach(function (f) { f.hidden = cat !== "all" && f.dataset.cat !== cat; });
    });
  }

  if (!lb || typeof lb.showModal !== "function") return;
  var d = lb.dataset, list = [], i = 0;
  lb.tabIndex = -1;
  lb.innerHTML = '<img alt=""><p aria-live="polite"></p>' +
    '<button type="button" class="prev" aria-label="' + d.prev + '">&#8249;</button>' +
    '<button type="button" class="next" aria-label="' + d.next + '">&#8250;</button>' +
    '<button type="button" class="x" aria-label="' + d.close + '">&#215;</button>';
  var img = lb.querySelector("img"), count = lb.querySelector("p");

  function show(n) {
    i = (n + list.length) % list.length;
    var a = list[i].querySelector("a"), thumb = a.querySelector("img");
    img.src = a.href; img.alt = thumb.alt;
    img.width = +a.dataset.w; img.height = +a.dataset.h;
    count.textContent = (i + 1) + " / " + list.length;
    var multi = list.length > 1;
    lb.querySelector(".prev").hidden = lb.querySelector(".next").hidden = !multi;
  }

  sec.querySelector(".wgrid").addEventListener("click", function (ev) {
    var a = ev.target.closest("a");
    if (!a) return;
    ev.preventDefault();
    list = figs.filter(function (f) { return !f.hidden; });
    show(list.indexOf(a.parentNode));
    lb.showModal();
    lb.focus();  // focus the viewer itself so no arrow button lights up on open
  });
  lb.querySelector(".prev").addEventListener("click", function () { show(i - 1); });
  lb.querySelector(".next").addEventListener("click", function () { show(i + 1); });
  lb.querySelector(".x").addEventListener("click", function () { lb.close(); });
  lb.addEventListener("click", function (ev) { if (ev.target === lb) lb.close(); });
  lb.addEventListener("keydown", function (ev) {
    if (ev.key === "ArrowLeft") show(i - 1);
    if (ev.key === "ArrowRight") show(i + 1);
  });
  var x0 = null;
  lb.addEventListener("touchstart", function (ev) { x0 = ev.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", function (ev) {
    if (x0 === null) return;
    var dx = ev.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(dx < 0 ? i + 1 : i - 1);
    x0 = null;
  });
})();
