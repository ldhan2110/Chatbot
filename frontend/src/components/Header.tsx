import {
  BellOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Avatar, Button, Divider, Dropdown, Flex } from "antd";
import React from "react";
import { Logo } from "./Logo";

type HeaderProps = {
  collapsed: boolean;
  toggleCollapsed: () => void;
};

export const Header = ({ collapsed, toggleCollapsed }: HeaderProps) => {
  // Random background color using useMemo so it doesn't change every render
  const randomBgColor = React.useMemo(() => {
    const randomColor = () =>
      "#" +
      Math.floor(Math.random() * 16777215)
        .toString(16)
        .padStart(6, "0");
    return randomColor();
  }, []);

  const onMenuClick = ({ key }: { key: string }) => {
    if (key === "profile") return "";
  };

  const userMenuItems = [
    { key: "profile", icon: <UserOutlined />, label: "Profile" },
    { type: "divider" as const },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "Logout",
      danger: true,
    },
  ];

  return (
    <>
      <div className="bg-white shadow-md h-16 px-4 flex items-center justify-between ">
        <Flex justify="space-between" className="w-full">
          <Flex gap={16}>
            <Flex align="center">
              <Button
                size="middle"
                type="primary"
                onClick={toggleCollapsed}
                className="ml-1"
              >
                {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              </Button>
            </Flex>
            <Logo />
          </Flex>
          <Flex justify="end" gap={4}>
            <Flex gap={8}>
              <Button
                shape="circle"
                icon={<BellOutlined />}
                style={{
                  marginTop: "5px",
                }}
              />
            </Flex>
            <Flex justify="center" align="center" gap={2}>
              <Divider type="vertical" size="middle" />
            </Flex>
            <Dropdown
              menu={{ items: userMenuItems, onClick: onMenuClick }}
              trigger={["click"]}
              placement="bottomRight"
              getPopupContainer={(triggerNode) =>
                triggerNode.parentElement || document.body
              }
            >
              <div
                className="flex items-center text-gray-700 cursor-pointer select-none self-center"
                tabIndex={0}
              >
                <Avatar
                  style={{ backgroundColor: randomBgColor, cursor: "pointer" }}
                >
                  {"A"}
                </Avatar>
                <span className="ml-2">
                  Hi, <span className="font-bold">{"Admin"}</span>
                </span>
              </div>
            </Dropdown>
          </Flex>
        </Flex>
      </div>
    </>
  );
};

export default Header;
