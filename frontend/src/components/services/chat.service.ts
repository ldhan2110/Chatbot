import { getChatSseUrl } from "@/libs/api";
import type { ChatRequest } from "@/types/system";

export async function sendChat(payload: ChatRequest, ac: AbortController) {
  const init = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal: ac.signal,
  };
  const res = await fetch(getChatSseUrl(), init);
  if (!res.ok || !res.body) {
    throw new Error(`Bad response: ${res.status}`);
  }

  return res;
}
