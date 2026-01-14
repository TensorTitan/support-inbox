import { GATEWAY_WS, getToken } from "./api.js";

export function connectWS({ onOpen, onClose, onMessage }) {
  const token = getToken();
  const url = `${GATEWAY_WS}?token=${encodeURIComponent(token)}`;

  const ws = new WebSocket(url);

  ws.onopen = () => onOpen?.();
  ws.onclose = () => onClose?.();

  ws.onmessage = (e) => {
    try {
      onMessage?.(JSON.parse(e.data));
    } catch {
    }
  };

  return ws;
}