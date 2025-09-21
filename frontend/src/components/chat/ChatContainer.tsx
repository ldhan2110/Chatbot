import { Avatar, Card, List, Space, Typography } from "antd";
import { Content } from "antd/es/layout/layout";
import React from "react";

export const ChatContainer = () => {
  const [messages] = React.useState([
    { sender: "assistant", text: "Hello! How can I help you today?" },
    {
      sender: "user",
      text: "I'm looking for a way to build a chat interface.",
    },
    {
      sender: "assistant",
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

  return (
    <Content className="p-6 flex flex-col overflow-y-auto">
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto p-4 bg-[#f5f5f5] rounded-xl"
      >
        <List
          itemLayout="horizontal"
          dataSource={messages}
          renderItem={(item) => (
            <List.Item
              style={{
                border: "none",
                padding: "8px 0",
                justifyContent:
                  item.sender === "user" ? "flex-end" : "flex-start",
              }}
            >
              <Space
                direction="horizontal"
                style={{
                  display: "flex",
                  flexDirection: item.sender === "user" ? "row-reverse" : "row",
                  alignItems: "flex-end",
                  maxWidth: "80%",
                }}
              >
                <Avatar
                  style={{
                    backgroundColor:
                      item.sender === "user" ? "#1890ff" : "#87d068",
                    flexShrink: 0,
                  }}
                  src={
                    item.sender === "user"
                      ? null
                      : "https://placehold.co/40x40/87d068/ffffff?text=AI"
                  }
                >
                  {item.sender === "user" ? "You" : ""}
                </Avatar>
                <Card
                  style={{
                    borderRadius: "16px",
                    border: "none",
                    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
                    backgroundColor:
                      item.sender === "user" ? "#e6f7ff" : "#fff",
                  }}
                  bodyStyle={{ padding: "12px 16px" }}
                >
                  <Typography.Text>{item.text}</Typography.Text>
                </Card>
              </Space>
            </List.Item>
          )}
        />
      </div>
    </Content>
  );
};
