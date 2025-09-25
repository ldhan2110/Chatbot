import { ConfigProvider, List } from "antd";
import { Content } from "antd/es/layout/layout";
import React from "react";
import { ChatBubble } from "./ChatBubble";
import { ChatInput } from "./ChatInput";
import type { ChatMessage } from "@/types/system";
export const ChatContainer = () => {
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const chatContainerRef = React.useRef(null);

  // Auto-scroll to the latest message
  React.useEffect(() => {
    if (chatContainerRef.current) {
      (chatContainerRef.current as HTMLDivElement).scrollTop = (
        chatContainerRef.current as HTMLDivElement
      ).scrollHeight;
    }
  }, [messages]);

  return (
    <Content
      className="flex flex-col overflow-y-auto"
      style={{
        height: "calc(100vh - 65px)",
      }}
    >
      <ConfigProvider
        renderEmpty={() => (
          <div className="text-center flex flex-col justify-center h-[calc(100vh-300px)] gap-0.5">
            <h1 className="text-3xl font-semibold text-blue-500">Welcome!</h1>
            <p className="text-xl text-gray-300">BluePrint Agents for CLT</p>
          </div>
        )}
      >
        <div
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto pl-[200px] pr-[200px] no-scrollbar bg-white"
        >
          <List
            style={{
              padding: "8px 32px",
            }}
            itemLayout="horizontal"
            dataSource={messages}
            renderItem={(item) => (
              <ChatBubble sender={item.role} message={item.content} />
            )}
          />
        </div>
        <ChatInput setMessages={setMessages} />
      </ConfigProvider>
    </Content>
  );
};
