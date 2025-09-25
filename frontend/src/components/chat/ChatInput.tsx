/* eslint-disable @typescript-eslint/no-explicit-any */
import { MessageRole, type ChatMessage } from "@/types/system";
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
import { sendChat } from "../services";
import { useChatStore } from "@/stores";

type ChatInputProps = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  setMessages: React.Dispatch<React.SetStateAction<any[]>>;
};

export const ChatInput = ({ setMessages }: ChatInputProps) => {
  const { currentConversationId, setCurrentConversation } = useChatStore();
  const [inputValue, setInputValue] = React.useState("");
  const [isStreaming, setIsStreaming] = React.useState<boolean>(false);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    setIsStreaming(true);

    const usrMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: MessageRole.USER,
      content: inputValue,
    };
    const assistantMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: MessageRole.ASSISTANT,
      content: "",
    };

    setMessages((prev) => [...prev, usrMsg, assistantMsg]);
    setInputValue("");

    // Send Request
    const ac = new AbortController();
    const res = await sendChat(
      {
        conversation_id: currentConversationId,
        message: usrMsg.content,
      },
      ac
    );

    const reader = res.body?.getReader();
    if (!reader) {
      throw new Error("ReadableStream is not available in this response");
    }

    const decoder: TextDecoder = new TextDecoder("utf-8");
    let buffer = "";

    // Read SSE stream manually and parse events
    //let sseError: Error | null = null;

    const commitChunk = (chunkContent: string) => {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMsg.id
            ? { ...m, content: m.content + chunkContent }
            : m
        )
      );
    };

    while (true) {
      const { done, value: chunk } = await reader.read();
      if (done) break;
      const bytes: any = chunk as any;
      buffer += decoder.decode(bytes, { stream: true });

      // Process complete SSE messages separated by double newlines
      let idx: number;
      while ((idx = buffer.indexOf("\n\n")) !== -1) {
        const rawEvent = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);

        // Parse event name and data lines
        const lines = rawEvent.split(/\r?\n/);
        let eventName = "message";
        const dataLines: string[] = [];
        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventName = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            dataLines.push(line.slice(5).trim());
          }
        }
        const dataStr = dataLines.join("\n");

        console.log(eventName, dataStr);

        if (eventName === "conversation_created") {
          try {
            const parsed = JSON.parse(dataStr) as {
              conversation_id?: string;
            };
            const cid = parsed?.conversation_id;
            if (cid) {
              setCurrentConversation(cid);
            }
          } catch {
            // ignore navigation errors
          }
        } else if (eventName === "ai_message") {
          try {
            const parsed = JSON.parse(dataStr) as {
              chunk?: { content?: string };
            };
            const chunk = parsed?.chunk?.content ?? "";
            if (chunk) {
              commitChunk(chunk);
            }
          } catch {
            // ignore parse errors per chunk
          }
        } else if (eventName === "error") {
          try {
            const err = JSON.parse(dataStr) as any;
            const detailsStr =
              typeof err?.details === "string" ? (err.details as string) : "";
            // Try to extract retry delay from provider details, e.g. "retryDelay': '55s'"
            const m = detailsStr.match(
              /retryDelay['\\"]?\s*:\s*['\\"](?<sec>\d+)s['\\"]/
            );
            const sec =
              m && m.groups && m.groups.sec ? Number(m.groups.sec) : undefined;
            const friendly =
              typeof sec === "number"
                ? `Hệ thống đang quá tải tạm thời. Vui lòng thử lại sau khoảng ${sec} giây.`
                : "Hệ thống đang quá tải tạm thời. Vui lòng thử lại sau ít phút.";
            //sseErrorInfo = { message: friendly, retryAfterSec: sec };
            // Show banner immediately for better UX
            //setErrorNotice({ message: friendly, retryAfterSec: sec });
            // Ensure assistant bubble shows a friendly message instead of AbortError
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantMsg.id
                  ? {
                      ...m,
                      content:
                        m.content && m.content.trim().length > 0
                          ? m.content
                          : `> ${friendly}`,
                    }
                  : m
              )
            );
            // sseError = new Error(friendly);
            // abort the stream; we'll throw after the loop ends
            try {
              ac.abort();
            } catch {
              // ignore error aborted
            }
          } catch {
            const friendly = "Something went wrong. Please try it again later.";
            // sseErrorInfo = { message: friendly };
            // setErrorNotice({ message: friendly });
            // sseError = new Error(friendly);
            console.log(friendly);
            try {
              ac.abort();
            } catch {
              // ignore error aborted
            }
          }
        }
      }
    }

    setIsStreaming(false);
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
                loading={isStreaming}
                onClick={handleSend}
              />
            </div>
          </Flex>
        </Flex>
      </div>
    </Flex>
  );
};
