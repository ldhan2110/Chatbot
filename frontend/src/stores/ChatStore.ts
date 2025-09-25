/* eslint-disable @typescript-eslint/no-unused-vars */
import { create } from "zustand";
import { devtools } from "zustand/middleware";

interface ChatStoreState {
  currentConversationId?: string;
  historyConversationList: string[];
  setCurrentConversation: (id: string) => void;
}

const INITIAL_STORES_STATE = {
  currentConversationId: undefined,
  historyConversationList: [],
};

export const useChatStore = create(
  devtools<ChatStoreState>((set) => ({
    ...INITIAL_STORES_STATE,
    setCurrentConversation: (id: string) => {
      set({
        currentConversationId: id,
      });
    },
  }))
);
