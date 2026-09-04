/*!
 * kai-player.js — reliable voice playback for Kai landing pages.
 *
 * Replaces the previous per-page inline script, which failed for real leads in
 * three ways:
 *
 *  1. RACE. The pages carried an `autoplay` attribute AND a window-load
 *     play() AND a button play(). Up to three play() calls competed with the
 *     element's own load, producing
 *     "AbortError: The play() request was interrupted by a new load request"
 *     — reproduced on the live Patricia page 2026-09-04. The button then
 *     looked dead even though the audio was fine.
 *
 *  2. FALSE CONFIDENCE. Chrome grants autoplay to domains the *local* user
 *     has engaged with (Media Engagement Index). It therefore played
 *     perfectly on Ivan's browser and was blocked for a cold lead opening the
 *     link from an SMS — the exact audience that matters.
 *
 *  3. SILENCE. Every failure was swallowed into one "Tap to play" string, so a
 *     404, a decode failure and an autoplay block were indistinguishable.
 *
 * Design: exactly one play path, serialised; never autoplay; treat the first
 * tap as both "load" and "play" (iOS ignores preload until a gesture); report
 * the real error class.
 */
(function () {
  'use strict';

  function init(root) {
    var audio = root.querySelector('audio[data-kai-audio]') || root.querySelector('audio');
    var button = root.querySelector('[data-kai-play]') || root.querySelector('.play-button');
    var label = root.querySelector('[data-kai-state]') || root.querySelector('#audioState');
    if (!audio || !button) return;

    var busy = false;          // serialises play(); the AbortError guard
    var started = false;

    function setState(text, kind) {
      if (label) label.textContent = text;
      button.setAttribute('data-state', kind || 'idle');
    }

    function log(event, detail) {
      // Observability: kept on the page so a failing lead session can be
      // diagnosed from a screenshot or a remote console, not guessed at.
      try {
        var line = '[kai-player] ' + event + (detail ? ' — ' + detail : '');
        (window.__kaiPlayerLog = window.__kaiPlayerLog || []).push(line);
        if (window.console && console.debug) console.debug(line);
      } catch (e) { /* logging must never break playback */ }
    }

    function describe(err) {
      if (!err) return 'unknown error';
      switch (err.name) {
        case 'NotAllowedError':
          return 'browser blocked playback — tap play';
        case 'NotSupportedError':
          return 'audio file missing or unplayable';
        case 'AbortError':
          return 'playback interrupted — tap play again';
        default:
          return err.name + ': ' + (err.message || '').slice(0, 120);
      }
    }

    // iOS Safari ignores preload until a user gesture, so the first tap must
    // wait for enough data before play() — otherwise play() rejects on a
    // still-empty element and the button reads as broken.
    function ready() {
      if (audio.readyState >= 3) return Promise.resolve();
      return new Promise(function (resolve, reject) {
        var done = false;
        var timer = setTimeout(function () {
          if (done) return;
          done = true;
          reject(new Error('timeout loading audio'));
        }, 15000);
        function ok() {
          if (done) return;
          done = true; clearTimeout(timer); cleanup(); resolve();
        }
        function bad() {
          if (done) return;
          done = true; clearTimeout(timer); cleanup();
          var e = new Error('network or decode error');
          e.name = 'NotSupportedError';
          reject(e);
        }
        function cleanup() {
          audio.removeEventListener('canplay', ok);
          audio.removeEventListener('loadeddata', ok);
          audio.removeEventListener('error', bad);
        }
        audio.addEventListener('canplay', ok);
        audio.addEventListener('loadeddata', ok);
        audio.addEventListener('error', bad);
        try { audio.load(); } catch (e) { bad(); }
      });
    }

    function toggle() {
      if (busy) { log('click ignored', 'play already in flight'); return; }

      if (started && !audio.paused) {
        audio.pause();
        setState('Paused — tap to resume', 'paused');
        return;
      }

      busy = true;
      setState('Loading…', 'loading');
      audio.muted = false;

      // play() MUST be called synchronously inside the click handler. Awaiting
      // canplay first (an earlier version of this file did) spends the user
      // gesture, so the later play() is rejected with NotAllowedError even
      // though the browser then starts the audio anyway — the button worked
      // but the label read "blocked". Call play() first; only fall back to
      // load-then-retry if the element genuinely had no data.
      var first = audio.play();
      (first && first.catch ? first : Promise.reject(new Error('no promise')))
        .catch(function (err) {
          if (err && err.name === 'NotAllowedError') throw err; // real block
          return ready().then(function () { return audio.play(); });
        })
        .then(function () {
          started = true;
          setState('Playing', 'playing');
          log('play ok', audio.currentSrc);
        })
        .catch(function (err) {
          setState(describe(err), 'error');
          log('play failed', describe(err));
        })
        .then(function () { busy = false; });
    }

    button.addEventListener('click', toggle);
    audio.addEventListener('ended', function () {
      started = false;
      setState('Replay', 'idle');
    });
    audio.addEventListener('error', function () {
      setState('Audio unavailable', 'error');
      log('element error', 'networkState=' + audio.networkState);
    });

    // Deliberately NO autoplay and NO load-time play(): both were unreliable
    // and were the source of the race. The button is the single entry point.
    audio.removeAttribute('autoplay');
    setState('Tap to play', 'idle');
    log('ready', audio.currentSrc || 'no src yet');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(document); });
  } else {
    init(document);
  }
})();
