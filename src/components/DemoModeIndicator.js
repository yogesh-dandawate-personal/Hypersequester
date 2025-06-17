import React from 'react';
import { Alert, Button, Space } from 'antd';
import { ExperimentOutlined, ApiOutlined } from '@ant-design/icons';
import { isDemoMode } from '../utils/demoData';

const DemoModeIndicator = () => {
  if (!isDemoMode()) {
    return null;
  }

  const handleExitDemo = () => {
    const url = new URL(window.location);
    url.searchParams.delete('demo');
    window.location.href = url.toString();
  };

  return (
    <Alert
      message="Demo Mode Active"
      description={
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <div>
            You're viewing Hypersequester in demo mode with sample data. 
            All features are functional but no real data processing occurs.
          </div>
          <Space>
            <Button 
              size="small" 
              icon={<ApiOutlined />}
              onClick={handleExitDemo}
            >
              Try Live API
            </Button>
            <Button 
              size="small" 
              type="link"
              href="https://github.com/Instoradmin/Hypersequester"
              target="_blank"
            >
              View Source Code
            </Button>
          </Space>
        </Space>
      }
      type="info"
      icon={<ExperimentOutlined />}
      showIcon
      closable
      style={{
        margin: '16px',
        borderRadius: '8px',
      }}
    />
  );
};

export default DemoModeIndicator;
