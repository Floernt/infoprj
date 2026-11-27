// Mesure d'audience Clicky, sans cookie (voir la page « À propos »).
var clicky_custom = clicky_custom || {};
clicky_custom.cookies_disable = 1;
(function() {
  var s = document.createElement('script');
  s.type = 'text/javascript';
  s.async = true;
  s.src = '//static.getclicky.com/js';
  s.setAttribute('data-id', '101514196');
  (document.head || document.body).appendChild(s);
})();

// Navigation instantanée : les changements de page ne rechargent pas le
// document, Clicky ne verrait que la page d'arrivée. On signale chaque
// navigation suivante comme une page vue.
(function() {
  if (typeof document$ === 'undefined') return;
  var first = true;
  document$.subscribe(function() {
    if (first) { first = false; return; }
    if (typeof clicky !== 'undefined' && clicky.log) {
      clicky.log(location.pathname + location.search, document.title, 'pageview');
    }
  });
})();
