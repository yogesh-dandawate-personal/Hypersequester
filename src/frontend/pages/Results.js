import React from 'react';
import { Typography, Card, Row, Col, Statistic } from 'antd';
import { BarChartOutlined, CloudOutlined, EnvironmentOutlined } from '@ant-design/icons';

const { Title } = Typography;

const Results = () => {
  return (
    <div>
      <Title level={2}>
        <BarChartOutlined style={{ marginRight: 8 }} />
        Assessment Results
      </Title>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Carbon Assessed"
              value={45680}
              suffix="tonnes CO₂"
              prefix={<CloudOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Total Area Assessed"
              value={2520}
              suffix="hectares"
              prefix={<EnvironmentOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Average Carbon Density"
              value={18.1}
              suffix="tonnes CO₂/ha"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Recent Results" size="small">
            <div style={{ padding: '16px 0' }}>
              <div style={{ marginBottom: 16 }}>
                <strong>Pacific Northwest Forest Reserve</strong>
                <br />
                <span style={{ color: '#666' }}>15,420 tonnes CO₂ • 1,250 ha</span>
                <br />
                <span style={{ fontSize: '12px', color: '#999' }}>Completed: June 15, 2024</span>
              </div>
              
              <div style={{ marginBottom: 16 }}>
                <strong>Cascade Mountain Timber</strong>
                <br />
                <span style={{ color: '#666' }}>12,340 tonnes CO₂ • 850 ha</span>
                <br />
                <span style={{ fontSize: '12px', color: '#999' }}>Completed: June 10, 2024</span>
              </div>
              
              <div>
                <strong>Willamette Valley Project</strong>
                <br />
                <span style={{ color: '#666' }}>7,920 tonnes CO₂ • 420 ha</span>
                <br />
                <span style={{ fontSize: '12px', color: '#999' }}>Completed: June 8, 2024</span>
              </div>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="Species Distribution" size="small">
            <div style={{ padding: '16px 0' }}>
              <div style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Douglas Fir</span>
                  <span>45%</span>
                </div>
                <div style={{ background: '#f0f0f0', height: 8, borderRadius: 4, marginTop: 4 }}>
                  <div style={{ background: '#52c41a', height: 8, width: '45%', borderRadius: 4 }}></div>
                </div>
              </div>
              
              <div style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Western Hemlock</span>
                  <span>30%</span>
                </div>
                <div style={{ background: '#f0f0f0', height: 8, borderRadius: 4, marginTop: 4 }}>
                  <div style={{ background: '#1890ff', height: 8, width: '30%', borderRadius: 4 }}></div>
                </div>
              </div>
              
              <div style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Red Cedar</span>
                  <span>15%</span>
                </div>
                <div style={{ background: '#f0f0f0', height: 8, borderRadius: 4, marginTop: 4 }}>
                  <div style={{ background: '#722ed1', height: 8, width: '15%', borderRadius: 4 }}></div>
                </div>
              </div>
              
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Other Species</span>
                  <span>10%</span>
                </div>
                <div style={{ background: '#f0f0f0', height: 8, borderRadius: 4, marginTop: 4 }}>
                  <div style={{ background: '#fa8c16', height: 8, width: '10%', borderRadius: 4 }}></div>
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Results;
