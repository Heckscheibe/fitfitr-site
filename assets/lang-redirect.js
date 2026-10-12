/* Start page language redirect.
   Loaded synchronously in <head> of the site root only, before the stylesheet,
   so a redirecting visitor never sees a painted page.
   Reads the browser's language list once, stores nothing and sends nothing.
   First listed language that is German or English wins; anything else goes to English. */
(function () {
  'use strict';

  var TARGETS = { de: '/de/', en: '/en/' };
  var DEFAULT_TARGET = '/en/';

  function primarySubtag(tag) {
    return String(tag).toLowerCase().split(/[-_]/)[0];
  }

  function pickTarget() {
    var list = [];
    try {
      var languages = navigator.languages;
      if (languages && languages.length) {
        list = Array.prototype.slice.call(languages);
      } else if (navigator.language) {
        list = [navigator.language];
      }
    } catch (e) {
      list = [];
    }
    for (var i = 0; i < list.length; i++) {
      var subtag = primarySubtag(list[i]);
      if (Object.prototype.hasOwnProperty.call(TARGETS, subtag)) {
        return TARGETS[subtag];
      }
    }
    return DEFAULT_TARGET;
  }

  try {
    location.replace(pickTarget());
  } catch (e) {
    /* leave the page as it is: it offers both languages as links */
  }
})();
