/* =====================================================================
   MentorLink — couche d'accès à l'API backend (FastAPI)
   Inclure ce fichier AVANT le script de chaque page :
   <script src="./assets/js/api.js"></script>
   ===================================================================== */

// 127.0.0.1 plutôt que localhost : évite la latence de résolution IPv6 (::1) sous Windows
const API_BASE = 'http://127.0.0.1:8000';

/* ---------- Gestion des tokens (localStorage) ---------- */
function setTokens(access, refresh) {
  if (access) localStorage.setItem('ml_token', access);
  if (refresh) localStorage.setItem('ml_refresh', refresh);
}
function getToken()   { return localStorage.getItem('ml_token'); }
function clearTokens(){ ['ml_token','ml_refresh','ml_me'].forEach(k => localStorage.removeItem(k)); }

/* ---------- Appel générique ---------- */
async function api(path, opts = {}) {
  const { method = 'GET', body, auth = true, form = false } = opts;
  const headers = {};
  let payload = body;

  if (form) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
    payload = new URLSearchParams(body).toString();
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }
  if (auth && getToken()) headers['Authorization'] = 'Bearer ' + getToken();

  let res = await fetch(API_BASE + path, { method, headers, body: payload });

  // Token expiré -> on tente un refresh puis on rejoue la requête
  if (res.status === 401 && auth) {
    if (await tryRefresh()) {
      headers['Authorization'] = 'Bearer ' + getToken();
      res = await fetch(API_BASE + path, { method, headers, body: payload });
    } else {
      redirectLogin();
      throw new Error('Session expirée');
    }
  }

  if (!res.ok) {
    let msg = 'Erreur (' + res.status + ')';
    try {
      const e = await res.json();
      if (typeof e.detail === 'string') msg = e.detail;
      else if (Array.isArray(e.detail)) msg = e.detail.map(x => x.msg || JSON.stringify(x)).join(', ');
    } catch (_) {}
    const err = new Error(msg); err.status = res.status; throw err;
  }

  if (res.status === 204) return null;
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

/* ---------- Upload de fichier (multipart) ---------- */
async function uploadFile(path, file, field = 'file') {
  const fd = new FormData();
  fd.append(field, file);
  const headers = {};
  if (getToken()) headers['Authorization'] = 'Bearer ' + getToken();
  let res = await fetch(API_BASE + path, { method: 'POST', headers, body: fd });
  if (res.status === 401 && await tryRefresh()) {
    headers['Authorization'] = 'Bearer ' + getToken();
    res = await fetch(API_BASE + path, { method: 'POST', headers, body: fd });
  }
  if (!res.ok) {
    let msg = 'Échec de l\'envoi';
    try { const e = await res.json(); if (e.detail) msg = typeof e.detail === 'string' ? e.detail : msg; } catch (_) {}
    throw new Error(msg);
  }
  return res.json();
}

/* ---------- Avatar (photo de profil ou image par défaut) ---------- */
function avatar(u) { return (u && u.photo_url) ? u.photo_url : './assets/img/profil.svg'; }

async function tryRefresh() {
  const rt = localStorage.getItem('ml_refresh');
  if (!rt) return false;
  try {
    const data = await api('/auth/refresh', { method: 'POST', body: { refresh_token: rt }, auth: false });
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch (_) { return false; }
}

/* ---------- Garde d'authentification ---------- */
function redirectLogin() {
  clearTokens();
  if (!location.pathname.endsWith('index.html')) location.href = 'index.html';
}
function requireAuth() { if (!getToken()) location.href = 'index.html'; }

/* ---------- Auth ---------- */
async function login(identifiant, password) {
  const data = await api('/auth/login', { method: 'POST', form: true, auth: false, body: { username: identifiant, password } });
  setTokens(data.access_token, data.refresh_token);
  return data;
}
async function registerUser(payload) {
  return api('/auth/register', { method: 'POST', body: payload, auth: false });
}
async function logout() {
  try { await api('/auth/logout', { method: 'POST' }); } catch (_) {}
  clearTokens();
  location.href = 'index.html#login';
}
function confirmLogout() {
  if (confirm('Voulez-vous vraiment vous déconnecter ?')) logout();
}

/* ---------- Utilisateurs (cache) ---------- */
let _me = null;
async function getMe(force) {
  if (_me && !force) return _me;
  _me = await api('/users/me');
  return _me;
}
const _userCache = {};
async function getUser(id) {
  if (_userCache[id]) return _userCache[id];
  const u = await api('/users/' + id);
  _userCache[id] = u;
  return u;
}

/* ---------- Conversations ---------- */
async function startConversation(userId) {
  // Réutilise une conversation existante à 2 si elle existe, sinon en crée une
  try {
    const me = await getMe();
    const convs = await api('/conversations/');
    const found = (convs || []).find(c =>
      c.participants && c.participants.length === 2 &&
      c.participants.includes(userId) && c.participants.includes(me.id));
    if (found) return found.id;
  } catch (_) {}
  const data = await api('/conversations/', { method: 'POST', body: [userId] });
  return data.conversation_id;
}
async function contactAndGo(userId) {
  try {
    const id = await startConversation(userId);
    location.href = 'chat.html?conv=' + id;
  } catch (err) { toast(err.message || 'Impossible de démarrer la conversation', 'error'); }
}

/* ---------- Notifications "toast" (remplace les alert) ---------- */
/* Style « snackbar » professionnel : pilule sombre centrée en bas, sans bordure,
   avec une pastille de couleur selon le type. */
function toast(message, type = 'info') {
  let c = document.getElementById('ml-toasts');
  if (!c) {
    c = document.createElement('div');
    c.id = 'ml-toasts';
    c.style.cssText = 'position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%);z-index:9999;'
      + 'display:flex;flex-direction:column;align-items:center;gap:.5rem;pointer-events:none;';
    document.body.appendChild(c);
  }
  // Couleur du TEXTE selon le type (pas de pastille)
  const colors = { error: '#f87171', success: '#4ade80', info: '#60a5fa' };
  const col = colors[type] || colors.info;
  const t = document.createElement('div');
  t.style.cssText = 'background:#1B2330;color:' + col + ';text-align:center;'
    + 'font:600 13.5px Poppins,sans-serif;padding:.7rem 1.15rem;border-radius:999px;'
    + 'box-shadow:0 12px 32px rgba(11,27,58,.30);max-width:90vw;opacity:0;transform:translateY(16px);'
    + 'transition:opacity .28s ease, transform .28s cubic-bezier(.2,.8,.2,1);pointer-events:auto;';
  t.textContent = message;
  c.appendChild(t);
  requestAnimationFrame(() => { t.style.opacity = '1'; t.style.transform = 'none'; });
  setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateY(16px)'; setTimeout(() => t.remove(), 300); }, 3400);
}

/* ---------- Badges du menu (Messages + Offres) ---------- */
function setBadge(id, n) {
  const el = document.getElementById(id);
  if (!el) return;
  if (n > 0) { el.textContent = n > 99 ? '99+' : n; el.style.display = ''; }
  else { el.style.display = 'none'; }
}

/* Met à jour les pastilles du menu :
   - Messages : nombre de PERSONNES (conversations) avec des messages non lus
                (1 personne -> 1, 2 personnes -> 2…)
   - Offres   : nombre de notifications « nouvelle offre / demande » non lues */
async function refreshBadges() {
  try {
    const convs = await api('/conversations/');
    const nb = (convs || []).filter(c => (c.messages_non_lus || 0) > 0).length;
    setBadge('msgBadge', nb);
  } catch (_) {}
  try {
    const data = await api('/users/me/notifications');
    const nb = (data.notifications || []).filter(
      n => !n.lu && (n.type === 'nouvelle_offre' || n.type === 'nouvelle_demande')
    ).length;
    setBadge('offreBadge', nb);
  } catch (_) {}
}

/* ---------- Suivi des annonces auxquelles on a déjà répondu ---------- */
/* Sert à griser « Proposer mon aide » / « Demander de l'aide » une fois le message envoyé. */
function helpedKey(kind, id) { return kind + ':' + id; }
function getHelped() {
  try { return JSON.parse(localStorage.getItem('ml_helped') || '[]'); }
  catch (_) { return []; }
}
function isHelped(kind, id) { return getHelped().includes(helpedKey(kind, id)); }
function markHelped(kind, id) {
  const list = getHelped();
  const k = helpedKey(kind, id);
  if (!list.includes(k)) { list.push(k); localStorage.setItem('ml_helped', JSON.stringify(list)); }
}

/* ---------- Visionneuse d'image plein écran (clic sur une photo) ---------- */
function showImage(url) {
  if (!url) return;
  const ov = document.createElement('div');
  ov.style.cssText = 'position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,.85);display:flex;'
    + 'align-items:center;justify-content:center;padding:2rem;cursor:zoom-out;opacity:0;transition:opacity .2s ease;';
  const img = document.createElement('img');
  img.src = url;
  img.style.cssText = 'max-width:92vw;max-height:92vh;object-fit:contain;border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,.5);';
  ov.appendChild(img);
  ov.addEventListener('click', () => { ov.style.opacity = '0'; setTimeout(() => ov.remove(), 200); });
  document.body.appendChild(ov);
  requestAnimationFrame(() => { ov.style.opacity = '1'; });
}

/* ---------- Petits utilitaires ---------- */
function esc(s) {
  return (s == null ? '' : String(s)).replace(/[&<>"]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c]));
}
function iconFor(matiere) {
  const m = (matiere || '').toLowerCase();
  if (m.includes('python') || m.includes('java') || m.includes('poo') || m.includes('program')) return 'code';
  if (m.includes('sql') || m.includes('données') || m.includes('donnees') || m.includes('base')) return 'database';
  if (m.includes('web') || m.includes('html')) return 'layout';
  if (m.includes('math') || m.includes('stat')) return 'calculator';
  if (m.includes('réseau') || m.includes('reseau')) return 'network';
  if (m.includes('algo')) return 'git-branch';
  if (m.includes('anglais')) return 'languages';
  return 'graduation-cap';
}
