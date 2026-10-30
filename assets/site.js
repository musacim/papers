document.addEventListener("click", function (e) {
  var btn = e.target.closest("button.copy");
  if (!btn) return;
  var text = document.getElementById(btn.dataset.copy).textContent;
  navigator.clipboard.writeText(text).then(function () {
    btn.textContent = "Copied";
    setTimeout(function () { btn.textContent = "Copy"; }, 1500);
  });
});
