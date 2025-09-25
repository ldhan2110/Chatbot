export enum SENDER {
  AI = "AI",
  USER = "USER",
}

export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system",
  TOOL = "tool",
}

export type ChatRequest = {
  conversation_id?: string;
  message: string;
};

export type ChatMessage = {
  id: string;
  role: MessageRole;
  content: string;
  toolName?: string;
};
