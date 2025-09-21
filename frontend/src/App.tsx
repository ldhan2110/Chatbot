import { Flex, Layout } from "antd";
import Header from "./components/Header";
import { ChatContainer } from "./components/chat/ChatContainer";
import { SideBarMenu } from "./components/SidebarMenu";
import React from "react";

function App() {
  const [collapsed, setCollapsed] = React.useState(true);
  function toggleCollapsed() {
    setCollapsed(!collapsed);
  }

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header collapsed={collapsed} toggleCollapsed={toggleCollapsed} />
      <Flex>
        <SideBarMenu collapsed={collapsed} />
        <ChatContainer />
      </Flex>
    </Layout>
  );
}

export default App;
