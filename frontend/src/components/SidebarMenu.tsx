import { EditOutlined } from "@ant-design/icons";
import { Menu } from "antd";

type SideBarMenuProps = {
  collapsed: boolean;
};

export const SideBarMenu = ({ collapsed = false }: SideBarMenuProps) => {
  function handleOpenMenu() {}

  return (
    <div
      style={{
        height: "calc(100vh - 65px)",
      }}
      className={`h-screen ${
        collapsed ? "w-[80px]" : "w-64"
      } bg-white shadow-lg transition-width duration-300 float-left`}
    >
      <Menu
        mode="inline"
        theme="light"
        selectedKeys={[]}
        inlineCollapsed={collapsed}
        items={[
          {
            key: "NEW CHAT",
            label: "New Chat",
            icon: <EditOutlined />,
          },
        ]}
        onClick={handleOpenMenu}
      />
    </div>
  );
};
