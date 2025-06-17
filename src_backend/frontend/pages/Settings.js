import React from 'react';
import { Typography, Card, Form, Input, Select, Switch, Button, Space } from 'antd';
import { SettingOutlined } from '@ant-design/icons';

const { Title } = Typography;
const { Option } = Select;

const Settings = () => {
  const [form] = Form.useForm();

  const onFinish = (values) => {
    console.log('Settings updated:', values);
  };

  return (
    <div>
      <Title level={2}>
        <SettingOutlined style={{ marginRight: 8 }} />
        Settings
      </Title>

      <Card title="Processing Settings" style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            defaultPixelSize: 1.0,
            processingTimeout: 3600,
            maxConcurrentJobs: 4,
            autoProcessing: true,
            emailNotifications: true,
          }}
        >
          <Form.Item
            label="Default Pixel Size (meters)"
            name="defaultPixelSize"
            help="Default spatial resolution for hyperspectral processing"
          >
            <Input type="number" step="0.1" />
          </Form.Item>

          <Form.Item
            label="Processing Timeout (seconds)"
            name="processingTimeout"
            help="Maximum time allowed for processing jobs"
          >
            <Input type="number" />
          </Form.Item>

          <Form.Item
            label="Max Concurrent Jobs"
            name="maxConcurrentJobs"
            help="Maximum number of simultaneous processing jobs"
          >
            <Select>
              <Option value={1}>1</Option>
              <Option value={2}>2</Option>
              <Option value={4}>4</Option>
              <Option value={8}>8</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Auto-start Processing"
            name="autoProcessing"
            valuePropName="checked"
            help="Automatically start processing when data is uploaded"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="Email Notifications"
            name="emailNotifications"
            valuePropName="checked"
            help="Receive email notifications when processing completes"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Save Settings
              </Button>
              <Button>
                Reset to Defaults
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      <Card title="Account Information">
        <Form layout="vertical">
          <Form.Item label="Username">
            <Input defaultValue="forest.manager" disabled />
          </Form.Item>

          <Form.Item label="Email">
            <Input defaultValue="manager@forestcarbon.org" disabled />
          </Form.Item>

          <Form.Item label="Role">
            <Input defaultValue="Forest Manager" disabled />
          </Form.Item>

          <Form.Item>
            <Button>Change Password</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Settings;
