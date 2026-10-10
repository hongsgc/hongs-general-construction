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
