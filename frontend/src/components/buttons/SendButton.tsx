import { SendOutlined } from "@ant-design/icons";
import { Button } from "antd";

type SendButtonProps = {
  onSend: () => void;
};

export const SendButton = ({ onSend }: SendButtonProps) => {
  return (
    <Button
      type="primary"
      shape="circle"
      onClick={onSend}
      icon={<SendOutlined />}
      style={{
        width: "48px",
        height: "48px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#1890ff",
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.15)",
      }}
    />
  );
};
