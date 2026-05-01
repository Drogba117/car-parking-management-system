const BASE = 'https://car-parking-management-system-production.up.railway.app';

function getToken() {
  return localStorage.getItem('park_token');
}

function setToken(token) {
  localStorage.setItem('park_token', token);
}

function removeToken() {
  localStorage.removeItem('park_token');
}

async function apiPost(path, body, auth = false) {
  let headers = { 'Content-Type': 'application/json' };
  if (auth) headers['Authorization'] = 'Bearer ' + getToken();

  let res = await fetch(BASE + path, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(body)
  });

  return res;
}

async function apiGet(path, auth = false) {
  let headers = {};
  if (auth) headers['Authorization'] = 'Bearer ' + getToken();

  let res = await fetch(BASE + path, {
    method: 'GET',
    headers: headers
  });

  return res;
}

async function apiDelete(path, auth = false) {
  let headers = {};
  if (auth) headers['Authorization'] = 'Bearer ' + getToken();

  let res = await fetch(BASE + path, {
    method: 'DELETE',
    headers: headers
  });

  return res;
}