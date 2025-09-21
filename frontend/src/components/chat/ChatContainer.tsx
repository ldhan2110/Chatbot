import { List } from "antd";
import { Content } from "antd/es/layout/layout";
import React from "react";
import { ChatBubble } from "./ChatBubble";
import { SENDER } from "@/types/system";
import { ChatInput } from "./ChatInput";

export const ChatContainer = () => {
  const [messages, setMessages] = React.useState([
    { sender: SENDER.AI, text: "Hello! How can I help you today?" },
    {
      sender: SENDER.USER,
      text: "I'm looking for a way to build a chat interface.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
    {
      sender: SENDER.AI,
      text: "You've come to the right place! This component will get you started.",
    },
  ]);
  const chatContainerRef = React.useRef(null);

  // Auto-scroll to the latest message
  React.useEffect(() => {
    if (chatContainerRef.current) {
      (chatContainerRef.current as HTMLDivElement).scrollTop = (
        chatContainerRef.current as HTMLDivElement
      ).scrollHeight;
    }
  }, [messages]);

  function handleSendMessage(message: string) {
    setMessages([
      ...messages,
      {
        sender: SENDER.USER,
        text: message,
      },
    ]);
  }

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

      <ChatInput onSend={handleSendMessage} />
    </Content>
  );
};
