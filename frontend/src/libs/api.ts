export function getApiBaseUrl(): string {
  // Vite dev server default; can be overridden via VITE_API_BASE
  const fromEnv = import.meta.env.VITE_API_BASE as string | undefined;
  if (fromEnv) {
    const hasProtocol = /^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(fromEnv);
    const urlWithProtocol = hasProtocol ? fromEnv : `https://${fromEnv}`;
    return urlWithProtocol.replace(/\/$/, "");
  }
  return "http://localhost:8000"; // FastAPI default port
}

export function getChatSseUrl(): string {
  return `${getApiBaseUrl()}/chat/stream`;
}
