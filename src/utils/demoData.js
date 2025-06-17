/**
 * Demo data for frontend when backend is not available
 * This allows the frontend to be fully functional on Netlify
 */

export const demoProperties = [
  {
    id: '1',
    name: 'Pacific Northwest Forest Reserve',
    location: 'Oregon, USA',
    area: 1250,
    ownerType: 'Government',
    landUse: 'Conservation',
    coordinates: [[-122.5, 45.5], [-122.4, 45.5], [-122.4, 45.6], [-122.5, 45.6]],
    centroidLat: 45.55,
    centroidLon: -122.45,
  },
  {
    id: '2',
    name: 'Cascade Mountain Timber',
    location: 'Washington, USA',
    area: 850,
    ownerType: 'Private',
    landUse: 'Forestry',
    coordinates: [[-121.5, 47.5], [-121.4, 47.5], [-121.4, 47.6], [-121.5, 47.6]],
    centroidLat: 47.55,
    centroidLon: -121.45,
  },
  {
    id: '3',
    name: 'Willamette Valley Carbon Project',
    location: 'Oregon, USA',
    area: 420,
    ownerType: 'NGO',
    landUse: 'Mixed',
    coordinates: [[-123.2, 44.8], [-123.1, 44.8], [-123.1, 44.9], [-123.2, 44.9]],
    centroidLat: 44.85,
    centroidLon: -123.15,
  },
];

export const demoAssessments = [
  {
    id: '1',
    assessmentId: 'ASS-2024-001',
    propertyId: '1',
    property: 'Pacific Northwest Forest Reserve',
    date: '2024-06-15',
    status: 'completed',
    progress: 100,
    carbon: 15420,
    confidence: 0.92,
    sensorInfo: 'AVIRIS-NG Hyperspectral Imager',
    processingTime: '45 minutes',
  },
  {
    id: '2',
    assessmentId: 'ASS-2024-002',
    propertyId: '2',
    property: 'Cascade Mountain Timber',
    date: '2024-06-16',
    status: 'processing',
    progress: 65,
    carbon: null,
    confidence: null,
    sensorInfo: 'HySpex VNIR-1800',
    processingTime: null,
  },
  {
    id: '3',
    assessmentId: 'ASS-2024-003',
    propertyId: '3',
    property: 'Willamette Valley Carbon Project',
    date: '2024-06-17',
    status: 'pending',
    progress: 0,
    carbon: null,
    confidence: null,
    sensorInfo: 'PRISMA Hyperspectral',
    processingTime: null,
  },
];

export const demoResults = {
  totalCarbonAssessed: 45680,
  totalAreaAssessed: 2520,
  averageCarbonDensity: 18.1,
  assessmentsCompleted: 28,
  recentResults: [
    {
      property: 'Pacific Northwest Forest Reserve',
      carbon: 15420,
      area: 1250,
      date: 'June 15, 2024',
      density: 12.3,
    },
    {
      property: 'Cascade Mountain Timber',
      carbon: 12340,
      area: 850,
      date: 'June 10, 2024',
      density: 14.5,
    },
    {
      property: 'Willamette Valley Project',
      carbon: 7920,
      area: 420,
      date: 'June 8, 2024',
      density: 18.9,
    },
  ],
  speciesDistribution: [
    { name: 'Douglas Fir', percentage: 45, color: '#52c41a' },
    { name: 'Western Hemlock', percentage: 30, color: '#1890ff' },
    { name: 'Red Cedar', percentage: 15, color: '#722ed1' },
    { name: 'Other Species', percentage: 10, color: '#fa8c16' },
  ],
};

export const demoDashboardStats = {
  totalProperties: 12,
  activeAssessments: 3,
  completedAssessments: 28,
  totalCarbon: 15420,
  systemStatus: {
    processingEngine: 'online',
    database: 'connected',
    storage: 'available',
    queueJobs: 2,
  },
  recentActivity: [
    '📊 Pacific Northwest Forest - Completed',
    '🔄 Oregon State Reserve - Processing',
    '📊 Cascade Mountains - Completed',
    '⏳ Willamette Valley - Pending',
  ],
};

export const demoUser = {
  id: '1',
  username: 'demo.user',
  email: 'demo@hypersequester.com',
  role: 'Forest Manager',
  name: 'Demo User',
};

// Demo mode detection
export const isDemoMode = () => {
  return (
    process.env.REACT_APP_DEMO_MODE === 'true' ||
    window.location.hostname.includes('netlify.app') ||
    window.location.search.includes('demo=true')
  );
};

// Demo API responses
export const demoApiResponses = {
  '/auth/login': { token: 'demo-token', user: demoUser },
  '/properties': demoProperties,
  '/assessments': demoAssessments,
  '/stats/dashboard': demoDashboardStats,
  '/stats/carbon-trends': demoResults,
};

// Demo delay simulation
export const simulateApiDelay = (ms = 500) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};
