import { SENDER } from "@/types/system";
import { Avatar, Card, List, Space, Typography } from "antd";

type ChatBubbleProps = {
  sender: SENDER;
  message: string;
};

export const ChatBubble = ({ sender, message }: ChatBubbleProps) => {
  return (
    <List.Item
      style={{
        border: "none",
        padding: "8px 0",
        justifyContent: sender === SENDER.USER ? "flex-end" : "flex-start",
      }}
    >
      <Space
        direction="horizontal"
        style={{
          display: "flex",
          flexDirection: sender === SENDER.USER ? "row-reverse" : "row",
          alignItems: "flex-end",
          maxWidth: "80%",
        }}
      >
        <Avatar
          style={{
            backgroundColor: sender === SENDER.USER ? "#1890ff" : "#87d068",
            flexShrink: 0,
          }}
          src={
            sender === SENDER.USER
              ? null
              : "https://placehold.co/40x40/87d068/ffffff?text=AI"
          }
        >
          {sender === SENDER.USER ? "You" : ""}
        </Avatar>
        <Card
          style={{
            borderRadius: "16px",
            border: "none",
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
            backgroundColor: sender === SENDER.USER ? "#e6f7ff" : "#fff",
          }}
          bodyStyle={{ padding: "12px 16px" }}
        >
          <Typography.Text>{message}</Typography.Text>
        </Card>
      </Space>
    </List.Item>
  );
};
