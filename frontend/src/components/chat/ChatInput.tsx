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
  onSend: (value: any) => void;
};

export const ChatInput = ({ onSend }: ChatInputProps) => {
  const [inputValue, setInputValue] = React.useState("");
  const handleSend = () => {
    if (!inputValue.trim()) return;
    onSend(inputValue);
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
