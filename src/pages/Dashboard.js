import React from 'react';
import { Row, Col, Card, Statistic, Typography, Space } from 'antd';
import {
  EnvironmentOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  CloudOutlined,
} from '@ant-design/icons';

const { Title } = Typography;

const Dashboard = () => {
  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Statistics Cards */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Total Properties"
                value={12}
                prefix={<EnvironmentOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Active Assessments"
                value={3}
                prefix={<ExperimentOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Completed Assessments"
                value={28}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="Total Carbon (tonnes CO₂)"
                value={15420}
                prefix={<CloudOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Recent Activity */}
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="Recent Assessments" size="small">
              <div style={{ padding: '16px 0' }}>
                <p>📊 Pacific Northwest Forest - Completed</p>
                <p>🔄 Oregon State Reserve - Processing</p>
                <p>📊 Cascade Mountains - Completed</p>
                <p>⏳ Willamette Valley - Pending</p>
              </div>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="System Status" size="small">
              <div style={{ padding: '16px 0' }}>
                <p>✅ Processing Engine: Online</p>
                <p>✅ Database: Connected</p>
                <p>✅ Storage: Available</p>
                <p>⚠️ Queue: 2 jobs pending</p>
              </div>
            </Card>
          </Col>
        </Row>

        {/* Welcome Message */}
        <Card>
          <Title level={4}>Welcome to Hypersequester</Title>
          <p>
            Your comprehensive hyperspectral forest carbon assessment platform. 
            Get started by adding a new property or creating a carbon assessment.
          </p>
        </Card>
      </Space>
    </div>
  );
};

export default Dashboard;
