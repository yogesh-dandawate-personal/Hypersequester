import React from 'react';
import { Layout, Typography, Space, Avatar, Dropdown } from 'antd';
import { UserOutlined, SettingOutlined, LogoutOutlined } from '@ant-design/icons';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

const Header = () => {
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
    },
  ];

  return (
    <AntHeader
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#001529',
        padding: '0 24px',
      }}
    >
      <Space align="center">
        <div
          style={{
            width: 32,
            height: 32,
            background: '#52c41a',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            fontWeight: 'bold',
            color: 'white',
          }}
        >
          🌲
        </div>
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          Hypersequester
        </Title>
      </Space>

      <Dropdown
        menu={{ items: userMenuItems }}
        placement="bottomRight"
        arrow
      >
        <Avatar
          style={{ backgroundColor: '#52c41a', cursor: 'pointer' }}
          icon={<UserOutlined />}
        />
      </Dropdown>
    </AntHeader>
  );
};

export default Header;
