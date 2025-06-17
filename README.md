# Hypersequester

A comprehensive hyperspectral forest carbon assessment platform that transforms 2D hyperspectral imagery into detailed 3D forest models with precise carbon pool estimations.

## Overview

Hypersequester serves forestry professionals, carbon credit markets, conservation organizations, and research institutions by providing scientifically accurate, automated forest carbon assessments using cutting-edge hyperspectral analysis.

## Features

- **Hyperspectral Data Processing**: Support for AVIRIS, HySpex, PRISMA, EnMAP formats
- **Species Identification**: 50+ forest species with regional variations
- **Carbon Pool Estimation**: Above-ground biomass, below-ground biomass, dead wood, litter
- **3D Forest Modeling**: Interactive visualization with individual tree segmentation
- **Web-Based Dashboard**: Role-based access with real-time visualization
- **Compliance Ready**: IPCC, VCS, Gold Standard compatible reporting

## Quick Start

### Frontend Only (Netlify Demo)
```bash
# Clone the repository
git clone https://github.com/yogesh-dandawate-personal/Hypersequester.git
cd Hypersequester

# Install frontend dependencies
npm install

# Run frontend in demo mode
npm start
```

### Full Stack Development
```bash
# Install all dependencies
pip install -r requirements.txt
npm install

# Run backend
python src/main.py

# Run frontend (in another terminal)
npm start
```

### Docker Deployment
```bash
# Run complete stack
docker-compose up --build
```

## Documentation

Comprehensive documentation is available in the `/docs` folder:

- [Product Requirements Document](docs/PRD_Hypersequester.md)
- [Implementation Plan](docs/Implementation_Plan_Hypersequester.md)
- [Development Phases & Milestones](docs/Development_Phases_Milestones.md)
- [Risk Assessment & Mitigation](docs/Risk_Assessment_Mitigation.md)
- [UI Design Specifications](docs/ForestCarbon_UI.md)

## Project Structure

```
Hypersequester/
├── src/                    # Integrated source code
│   ├── backend/           # Flask API and services
│   │   ├── app.py         # Flask application factory
│   │   ├── models.py      # Database models
│   │   ├── routes.py      # API endpoints
│   │   └── tasks.py       # Background processing
│   ├── core/              # Core spectral processing algorithms
│   │   ├── processor.py   # Main processing engine
│   │   └── SpectralCarbonPoolEstimator.py
│   ├── models/            # Machine learning models
│   │   ├── species_classifier.py
│   │   └── carbon_estimator.py
│   ├── utils/             # Utility functions
│   │   ├── helpers.py     # Python utilities
│   │   ├── api.js         # Frontend API client
│   │   └── demoData.js    # Demo mode data
│   ├── components/        # React components
│   ├── pages/             # React pages
│   ├── hooks/             # React hooks
│   ├── styles/            # CSS styles
│   ├── App.js             # React app entry
│   ├── index.js           # Frontend entry point
│   └── main.py            # Backend entry point
├── public/                # Static files
├── tests/                 # Test suites
├── config/                # Configuration files
├── scripts/               # Build and deployment scripts
├── docs/                  # Documentation
└── README.md
```

## Contributing

Please read our [Implementation Plan](docs/Implementation_Plan_Hypersequester.md) for details on our development process and how to contribute.

## License

This project is licensed under the MIT License - see the LICENSE file for details.