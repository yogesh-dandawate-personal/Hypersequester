import React from 'react';
import { Typography, Button, Table, Space, Tag } from 'antd';
import { PlusOutlined, EnvironmentOutlined } from '@ant-design/icons';

const { Title } = Typography;

const Properties = () => {
  // Sample data
  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: 'Area (hectares)',
      dataIndex: 'area',
      key: 'area',
      render: (area) => `${area} ha`,
    },
    {
      title: 'Owner Type',
      dataIndex: 'ownerType',
      key: 'ownerType',
      render: (type) => (
        <Tag color={type === 'Government' ? 'blue' : type === 'Private' ? 'green' : 'orange'}>
          {type}
        </Tag>
      ),
    },
    {
      title: 'Land Use',
      dataIndex: 'landUse',
      key: 'landUse',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button type="link" size="small">View</Button>
          <Button type="link" size="small">Edit</Button>
          <Button type="link" size="small">Assess</Button>
        </Space>
      ),
    },
  ];

  const data = [
    {
      key: '1',
      name: 'Pacific Northwest Forest Reserve',
      location: 'Oregon, USA',
      area: 1250,
      ownerType: 'Government',
      landUse: 'Conservation',
    },
    {
      key: '2',
      name: 'Cascade Mountain Timber',
      location: 'Washington, USA',
      area: 850,
      ownerType: 'Private',
      landUse: 'Forestry',
    },
    {
      key: '3',
      name: 'Willamette Valley Carbon Project',
      location: 'Oregon, USA',
      area: 420,
      ownerType: 'NGO',
      landUse: 'Mixed',
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2}>
          <EnvironmentOutlined style={{ marginRight: 8 }} />
          Properties
        </Title>
        <Button type="primary" icon={<PlusOutlined />}>
          Add Property
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) =>
            `${range[0]}-${range[1]} of ${total} properties`,
        }}
      />
    </div>
  );
};

export default Properties;
