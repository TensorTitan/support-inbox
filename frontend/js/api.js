// frontend/js/api.js
export const GATEWAY_HTTP = "http://localhost:8000";
export const GATEWAY_WS = "ws://localhost:8000/ws";
export const MESSAGING_HTTP = "http://localhost:8001";

export function saveToken(token, name) {
  localStorage.setItem("token", token);
  localStorage.setItem("name", name || "");
}

export function getToken() {
  return localStorage.getItem("token");
}

export function getName() {
  return localStorage.getItem("name") || "";
}

export function clearAuth() {
  localStorage.removeItem("token");
  localStorage.removeItem("name");
}

export async function login(username, password) {
  const res = await fetch(`${GATEWAY_HTTP}/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ username, password })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Login failed");
  }
  return res.json();
}