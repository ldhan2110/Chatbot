/* eslint-disable @typescript-eslint/no-explicit-any */
import { MessageRole } from "@/types/system";
import { Avatar, Card, List, Space } from "antd";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";

type ChatBubbleProps = {
  sender: MessageRole;
  message: string;
};

const components = {
  code({ inline, className, children, ...props }: any) {
    const match = /language-(\w+)/.exec(className || "");
    return !inline && match ? (
      <SyntaxHighlighter language={match[1]} PreTag="div" {...props}>
        {String(children).replace(/\n$/, "")}
      </SyntaxHighlighter>
    ) : (
      <code {...props}>{children}</code>
    );
  },
};

export const ChatBubble = ({ sender, message }: ChatBubbleProps) => {
  return (
    <List.Item
      style={{
        border: "none",
        padding: "8px 0",
        justifyContent: sender === MessageRole.USER ? "flex-end" : "flex-start",
      }}
    >
      <Space
        direction="horizontal"
        style={{
          display: "flex",
          flexDirection: sender === MessageRole.USER ? "row-reverse" : "row",
          alignItems: "flex-end",
          maxWidth: "80%",
        }}
      >
        <Avatar
          style={{
            backgroundColor:
              sender === MessageRole.USER ? "#1890ff" : "#87d068",
            flexShrink: 0,
          }}
          src={
            sender === MessageRole.USER
              ? null
              : "https://placehold.co/40x40/87d068/ffffff?text=AI"
          }
        >
          {sender === MessageRole.USER ? "You" : ""}
        </Avatar>
        <Card
          style={{
            borderRadius: "16px",
            border: "none",
            boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
            backgroundColor: sender === MessageRole.USER ? "#e6f7ff" : "#fff",
          }}
          bodyStyle={{ padding: "12px 16px" }}
        >
          <ReactMarkdown components={components}>{message}</ReactMarkdown>
        </Card>
      </Space>
    </List.Item>
  );
};
