/* Consent banner and opt-in analytics.
   The only file that may talk to another host. Nothing is requested from Google until the visitor
   presses "Accept", and the choice is remembered as the word granted or denied in localStorage.
   While MEASUREMENT_ID is the placeholder, this file does nothing: no banner, no request.
   One event is sent besides page views: app_store_click, when a visitor who agreed follows a link marked
   data-store, with a fixed placement word (hero, final or guide) and the page language. Nothing else.
   The site is fully readable without this file. */
(function () {
  'use strict';

  var MEASUREMENT_ID = 'G-9NC65YPN99';
  var KEY = 'fitfitr-consent';

  if (!/^G-[A-Z0-9]{6,}$/.test(MEASUREMENT_ID) || /^G-X+$/.test(MEASUREMENT_ID)) {
    return;
  }

  var de = document.documentElement.lang === 'de';
  var T = de ? {
    label: 'Statistik',
    text: 'Darf diese Website anonyme Nutzungsstatistik mit Google Analytics erfassen? Ohne deine Zustimmung wird nichts an Google gesendet.',
    more: 'Datenschutzerklärung',
    href: '/de/datenschutz/#website',
    accept: 'Zustimmen',
    decline: 'Ablehnen',
    settings: 'Datenschutzeinstellungen'
  } : {
    label: 'Statistics',
    text: 'May this website collect anonymous usage statistics with Google Analytics? Nothing is sent to Google unless you agree.',
    more: 'Privacy policy',
    href: '/en/privacy/#website',
    accept: 'Accept',
    decline: 'Decline',
    settings: 'Privacy settings'
  };

  function read() {
    try {
      var v = window.localStorage.getItem(KEY);
      return v === 'granted' || v === 'denied' ? v : null;
    } catch (e) {
      return null;
    }
  }

  function write(v) {
    try {
      window.localStorage.setItem(KEY, v);
    } catch (e) {
      /* storage unavailable: the choice then lasts for this page view only */
    }
  }

  var loaded = false;

  function load() {
    if (loaded) {
      return;
    }
    loaded = true;
    window['ga-disable-' + MEASUREMENT_ID] = false;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', {
      analytics_storage: 'denied',
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied'
    });
    window.gtag('js', new Date());
    window.gtag('consent', 'update', { analytics_storage: 'granted' });
    window.gtag('config', MEASUREMENT_ID, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(MEASUREMENT_ID);
    document.head.appendChild(s);
  }

  function clearCookies() {
    var names = ['_ga', '_ga_' + MEASUREMENT_ID.replace(/^G-/, '')];
    var host = window.location.hostname;
    var domains = ['', host, '.' + host, '.fitfitr.app'];
    for (var i = 0; i < names.length; i++) {
      for (var j = 0; j < domains.length; j++) {
        document.cookie = names[i] + '=; Max-Age=0; path=/' + (domains[j] ? '; domain=' + domains[j] : '');
      }
    }
  }

  function unload() {
    window['ga-disable-' + MEASUREMENT_ID] = true;
    clearCookies();
  }

  var banner = null;

  function hide() {
    if (banner && banner.parentNode) {
      banner.parentNode.removeChild(banner);
    }
    banner = null;
  }

  function choose(value) {
    write(value);
    hide();
    if (value === 'granted') {
      load();
    } else {
      unload();
    }
  }

  function button(label, value) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'consent-button';
    b.textContent = label;
    b.addEventListener('click', function () { choose(value); });
    return b;
  }

  function show() {
    if (banner) {
      return;
    }
    banner = document.createElement('section');
    banner.className = 'consent';
    banner.setAttribute('aria-label', T.label);

    var p = document.createElement('p');
    p.className = 'consent-text';
    p.appendChild(document.createTextNode(T.text + ' '));
    var a = document.createElement('a');
    a.href = T.href;
    a.textContent = T.more;
    p.appendChild(a);

    var row = document.createElement('div');
    row.className = 'consent-actions';
    row.appendChild(button(T.decline, 'denied'));
    row.appendChild(button(T.accept, 'granted'));

    banner.appendChild(p);
    banner.appendChild(row);
    document.body.appendChild(banner);
  }

  function addFooterLink() {
    var nav = document.querySelector('.footer-nav');
    if (!nav) {
      return;
    }
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'footer-link';
    b.textContent = T.settings;
    b.addEventListener('click', show);
    nav.appendChild(b);
  }

  var PLACEMENTS = { hero: 1, final: 1, guide: 1 };

  function trackStoreClick(event) {
    var el = event.target && event.target.closest ? event.target.closest('a[data-store]') : null;
    var placement = el ? el.getAttribute('data-store') : null;
    if (!loaded || !window.gtag || window['ga-disable-' + MEASUREMENT_ID] || !PLACEMENTS[placement]) {
      return;
    }
    window.gtag('event', 'app_store_click', {
      placement: placement,
      language: de ? 'de' : 'en',
      transport_type: 'beacon'
    });
  }

  function init() {
    document.addEventListener('click', trackStoreClick);
    addFooterLink();
    var stored = read();
    if (stored === 'granted') {
      load();
    } else if (stored === null) {
      show();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
