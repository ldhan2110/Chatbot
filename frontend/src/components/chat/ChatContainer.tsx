import { List } from "antd";
import { Content } from "antd/es/layout/layout";
import React from "react";
import { ChatBubble } from "./ChatBubble";
import { ChatInput } from "./ChatInput";
export const ChatContainer = () => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [messages, setMessages] = React.useState<any[]>([]);
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
            <ChatBubble sender={item.sender} message={item.text} />
          )}
        />
      </div>

      <ChatInput setMessages={setMessages} />
    </Content>
  );
};
