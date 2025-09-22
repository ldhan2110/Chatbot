import { SENDER } from "@/types/system";
import {
  AudioOutlined,
  FileTextOutlined,
  PictureOutlined,
  PlusOutlined,
  SendOutlined,
  VideoCameraOutlined,
} from "@ant-design/icons";
import { Button, Flex, Input, Tooltip } from "antd";
import React from "react";

type ChatInputProps = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  setMessages: React.Dispatch<React.SetStateAction<any[]>>;
};

export const ChatInput = ({ setMessages }: ChatInputProps) => {
  const [inputValue, setInputValue] = React.useState("");
  const handleSend = () => {
    if (!inputValue.trim()) return;
    setMessages((prev) => [
      ...prev,
      {
        text: inputValue,
        sender: SENDER.USER,
      },
      { sender: SENDER.AI, text: "" },
    ]);
    const evtSource = new EventSource(
      `http://localhost:8000/chat/stream?prompt=${encodeURIComponent(
        inputValue
      )}`
    );

    evtSource.addEventListener("ai_message", (event) => {
      const data = JSON.parse(event.data);
      console.log(data.chunk.content);
      setMessages((prev) => {
        const last = prev[prev.length - 1];

        if (last && last.sender === SENDER.AI) {
          // Append chunk to last AI message
          return [
            ...prev.slice(0, -1),
            { ...last, text: last.text + data.chunk.content },
          ];
        }

        // Start new AI message with empty text,
        // then append first chunk in the next render
        return [...prev, { sender: SENDER.AI, text: data.chunk.content }];
      });
    });

    evtSource.addEventListener("done", () => {
      console.log("Stream finished");
      evtSource.close();
    });

    evtSource.onerror = (error) => {
      console.error("SSE error:", error);
      evtSource.close();
    };

    // push placeholder for streamed response
    setInputValue("");
  };
  return (
    <Flex
      justify="center"
      className="bg-white"
      style={{
        padding: "8px 0px",
      }}
    >
      <div className="w-[70%] px-4 py-2 border border-[#F9F9F9] rounded-2xl bg-white flex items-center space-x-2 shadow-sm">
        <Flex vertical className="w-full">
          {/* Input field */}
          <Input.TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask anything"
            autoSize={{ minRows: 1, maxRows: 4 }}
            bordered={false}
            className="flex-1 resize-none focus:ring-0 focus:outline-none"
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />

          <Flex justify="space-between">
            <div className="flex items-center space-x-3 text-gray-500">
              <Tooltip title="Add">
                <PlusOutlined className="text-lg cursor-pointer hover:text-blue-500" />
              </Tooltip>
              <Tooltip title="Video">
                <VideoCameraOutlined className="text-lg cursor-pointer hover:text-blue-500" />
              </Tooltip>
              <Tooltip title="Image">
                <PictureOutlined className="text-lg cursor-pointer hover:text-blue-500" />
              </Tooltip>
              <Tooltip title="File">
                <FileTextOutlined className="text-lg cursor-pointer hover:text-blue-500" />
              </Tooltip>
            </div>
            {/* Right icons */}
            <div className="flex items-center space-x-3 text-gray-500">
              <Tooltip title="Mic">
                <AudioOutlined className="text-lg cursor-pointer hover:text-blue-500" />
              </Tooltip>
              <Button
                type="primary"
                shape="circle"
                icon={<SendOutlined />}
                onClick={handleSend}
              />
            </div>
          </Flex>
        </Flex>
      </div>
    </Flex>
  );
};
