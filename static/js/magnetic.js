// Lightweight "magnetic pull" hover effect (no dependencies).
// Any element with the .magnetic class shifts slightly toward the cursor as
// it hovers, then snaps back on mouseleave (snap-back handled by CSS
// transition). Respects prefers-reduced-motion.
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) return;

  var STRENGTH = 0.35; // how strongly the element follows the cursor (0-1)
  var MAX = 14;        // max px offset in any direction

  function clamp(v, max) {
    return Math.max(-max, Math.min(max, v));
  }

  function attach(el) {
    el.addEventListener("mousemove", function (e) {
      var rect = el.getBoundingClientRect();
      var dx = e.clientX - (rect.left + rect.width / 2);
      var dy = e.clientY - (rect.top + rect.height / 2);
      var x = clamp(dx * STRENGTH, MAX);
      var y = clamp(dy * STRENGTH, MAX);
      el.style.transform = "translate(" + x + "px, " + y + "px)";
    });
    el.addEventListener("mouseleave", function () {
      el.style.transform = "";
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".magnetic").forEach(attach);
  });
})();
