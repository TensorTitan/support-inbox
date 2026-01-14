// frontend/js/login.js
import { login, saveToken } from "./api.js";

const u = document.getElementById("username");
const p = document.getElementById("password");
const btn = document.getElementById("loginBtn");
const errDiv = document.getElementById("error");

btn.onclick = async () => {
  errDiv.textContent = "";
  try {
    const data = await login(u.value.trim(), p.value);
    saveToken(data.access_token, data.name);
    window.location.href = "index.html";
  } catch (e) {
    errDiv.textContent = e.message;
  }
};