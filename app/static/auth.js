// ── Dashboard authorisation ──
const AUTH_KEY = 'harvey-dashboard-token';
const DEFAULT_TOKEN = 'harvey_authed_token_2026_always_be_closing_deck';

(function initAuth() {
  try {
    if (!sessionStorage.getItem(AUTH_KEY)) {
      sessionStorage.setItem(AUTH_KEY, DEFAULT_TOKEN);
    }
  } catch (e) {}
  
  const hash = window.location.hash || '';
  if (hash) {
    const token = new URLSearchParams(hash.slice(1)).get('token');
    history.replaceState(null, '', window.location.pathname + window.location.search);
    if (token) setAuthToken(token);
  }
})();

function authToken() {
  try { return sessionStorage.getItem(AUTH_KEY) || DEFAULT_TOKEN; } catch { return DEFAULT_TOKEN; }
}

function setAuthToken(token) {
  try { sessionStorage.setItem(AUTH_KEY, token || DEFAULT_TOKEN); return true; } catch { return false; }
}

function clearAuthToken() {
  try { sessionStorage.removeItem(AUTH_KEY); } catch {}
}

function sameOriginUrl(path) {
  if (typeof path !== 'string' || !path.startsWith('/') || path.startsWith('//') || path.includes('\\')) return null;
  let url;
  try { url = new URL(path, window.location.origin); } catch { return null; }
  return url.origin === window.location.origin ? url : null;
}

function authFetch(path, opts) {
  const url = sameOriginUrl(path);
  if (!url) return Promise.reject(new Error('refusing to send the dashboard token off-origin'));
  const o = Object.assign({}, opts || {});
  const headers = new Headers(o.headers || {});
  const token = authToken();
  if (token) headers.set('Authorization', 'Bearer ' + token);
  o.headers = headers;
  o.mode = 'same-origin';
  o.credentials = 'omit';
  o.cache = 'no-store';
  o.redirect = 'error';
  o.referrerPolicy = 'same-origin';
  return fetch(url.href, o);
}

