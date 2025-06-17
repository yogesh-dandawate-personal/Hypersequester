import React from 'react';
import { Typography, Button, Table, Space, Tag, Progress } from 'antd';
import { PlusOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Title } = Typography;

const Assessments = () => {
  const columns = [
    {
      title: 'Assessment ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Property',
      dataIndex: 'property',
      key: 'property',
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          'Completed': 'success',
          'Processing': 'processing',
          'Pending': 'warning',
          'Failed': 'error',
        };
        return <Tag color={colors[status]}>{status}</Tag>;
      },
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress, record) => (
        record.status === 'Processing' ? 
          <Progress percent={progress} size="small" /> : 
          record.status === 'Completed' ? 
            <Progress percent={100} size="small" status="success" /> :
            <span>-</span>
      ),
    },
    {
      title: 'Carbon (tonnes CO₂)',
      dataIndex: 'carbon',
      key: 'carbon',
      render: (carbon) => carbon ? `${carbon.toLocaleString()}` : '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button type="link" size="small">View</Button>
          {record.status === 'Completed' && (
            <Button type="link" size="small">Download</Button>
          )}
          {record.status === 'Failed' && (
            <Button type="link" size="small">Retry</Button>
          )}
        </Space>
      ),
    },
  ];

  const data = [
    {
      key: '1',
      id: 'ASS-2024-001',
      property: 'Pacific Northwest Forest Reserve',
      date: '2024-06-15',
      status: 'Completed',
      progress: 100,
      carbon: 15420,
    },
    {
      key: '2',
      id: 'ASS-2024-002',
      property: 'Cascade Mountain Timber',
      date: '2024-06-16',
      status: 'Processing',
      progress: 65,
      carbon: null,
    },
    {
      key: '3',
      id: 'ASS-2024-003',
      property: 'Willamette Valley Carbon Project',
      date: '2024-06-17',
      status: 'Pending',
      progress: 0,
      carbon: null,
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2}>
          <ExperimentOutlined style={{ marginRight: 8 }} />
          Carbon Assessments
        </Title>
        <Button type="primary" icon={<PlusOutlined />}>
          New Assessment
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
            `${range[0]}-${range[1]} of ${total} assessments`,
        }}
      />
    </div>
  );
};

export default Assessments;
