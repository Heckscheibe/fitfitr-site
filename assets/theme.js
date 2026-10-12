/* Light and dark switch.
   Loaded synchronously in <head> so the stored choice is applied before first paint.
   Stores only the string "light" or "dark" in localStorage under one key.
   The site is fully readable without this file. */
(function () {
  'use strict';

  var KEY = 'fitfitr-theme';
  var root = document.documentElement;

  root.classList.add('js');

  function readStored() {
    try {
      var value = window.localStorage.getItem(KEY);
      return value === 'light' || value === 'dark' ? value : null;
    } catch (e) {
      return null;
    }
  }

  function writeStored(value) {
    try {
      window.localStorage.setItem(KEY, value);
    } catch (e) {
      /* storage unavailable: the choice then lasts for this page view only */
    }
  }

  function systemPrefersDark() {
    return !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
  }

  function currentTheme() {
    var set = root.getAttribute('data-theme');
    if (set === 'light' || set === 'dark') {
      return set;
    }
    return systemPrefersDark() ? 'dark' : 'light';
  }

  var stored = readStored();
  if (stored) {
    root.setAttribute('data-theme', stored);
  }

  function updateButtons() {
    var theme = currentTheme();
    var buttons = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      var button = buttons[i];
      var label = theme === 'dark'
        ? button.getAttribute('data-label-to-light')
        : button.getAttribute('data-label-to-dark');
      if (label) {
        button.setAttribute('aria-label', label);
        button.setAttribute('title', label);
      }
    }
  }

  function toggle() {
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    writeStored(next);
    updateButtons();
  }

  function init() {
    var buttons = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener('click', toggle);
    }
    updateButtons();

    if (window.matchMedia) {
      var query = window.matchMedia('(prefers-color-scheme: dark)');
      var onChange = function () { updateButtons(); };
      if (query.addEventListener) {
        query.addEventListener('change', onChange);
      } else if (query.addListener) {
        query.addListener(onChange);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
