/* Board only: on a phone-sized window, scale the device frame so one whole phone fits the width. */
(function () {
  var root = document.documentElement;
  function fit() {
    var w = parseFloat(getComputedStyle(root).getPropertyValue('--device-w')) || 390;
    var vw = root.clientWidth;
    if (vw <= 480) root.style.setProperty('--device-scale', Math.min(1, (vw - 16) / w).toFixed(4));
    else root.style.removeProperty('--device-scale');
  }
  fit();
  window.addEventListener('resize', fit);
  window.addEventListener('orientationchange', fit);
})();
