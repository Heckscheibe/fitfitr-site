/* Entrance motion for the landing page: the charts draw in, the headline underline swipes, the step rules draw.
   Loaded synchronously in <head> so the hidden starting state is in place before first paint.
   Does nothing when the visitor asks for reduced motion, and the page is fully visible without it. */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    return;
  }

  root.classList.add('motion');

  function start() {
    var cards = document.querySelectorAll('#stories .lp-card .anim');
    for (var i = 0; i < cards.length; i += 1) {
      cards[i].style.setProperty('--stag', (i % 3) * 0.12 + 's');
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });

    document.querySelectorAll('.anim, .lp-steps').forEach(function (el) {
      io.observe(el);
    });

    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        root.classList.add('ready');
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
