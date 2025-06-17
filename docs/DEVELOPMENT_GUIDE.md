# Hypersequester Development Guide

This guide provides comprehensive information for developers working on the Hypersequester project.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Contributing](#contributing)

## Project Overview

Hypersequester is a comprehensive hyperspectral forest carbon assessment platform that transforms 2D hyperspectral imagery into detailed 3D forest models with precise carbon pool estimations.

### Key Features

- **Hyperspectral Data Processing**: Support for AVIRIS, HySpex, PRISMA, EnMAP formats
- **Species Identification**: Machine learning-based forest species classification
- **Carbon Pool Estimation**: Above-ground biomass, below-ground biomass, dead wood, litter
- **3D Forest Modeling**: Interactive visualization with individual tree segmentation
- **Web-Based Dashboard**: Role-based access with real-time visualization
- **Compliance Ready**: IPCC, VCS, Gold Standard compatible reporting

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Processing    │
│   (React.js)    │◄──►│   (Flask)       │◄──►│   (Celery)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   PostgreSQL    │    │     Redis       │
│   (Nginx)       │    │   (Database)    │    │   (Queue)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

**Backend:**
- Python 3.9+
- Flask (Web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Celery (Background tasks)
- Redis (Message broker)

**Frontend:**
- React.js 18
- Ant Design (UI components)
- Leaflet (Mapping)
- Three.js (3D visualization)
- Axios (HTTP client)

**Processing:**
- NumPy, SciPy (Scientific computing)
- Scikit-learn (Machine learning)
- Spectral (Hyperspectral processing)
- GDAL/Rasterio (Geospatial data)

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Git

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Instoradmin/Hypersequester.git
   cd Hypersequester
   ```

2. **Run the setup script:**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Start the development environment:**
   ```bash
   # Option 1: Using Docker (recommended)
   docker-compose up --build
   
   # Option 2: Manual setup
   source venv/bin/activate
   python src/main.py
   ```

4. **Access the application:**
   - Main application: http://localhost:5000
   - API documentation: http://localhost:5000/api/docs

### Manual Setup

If you prefer manual setup:

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database:**
   ```bash
   createdb hypersequester_dev
   python src/manage.py db upgrade
   ```

6. **Start services:**
   ```bash
   # Terminal 1: Start Redis
   redis-server
   
   # Terminal 2: Start Celery worker
   celery -A src.backend.tasks worker --loglevel=info
   
   # Terminal 3: Start Flask application
   python src/main.py
   
   # Terminal 4: Start frontend development server
   npm start
   ```

## Project Structure

```
Hypersequester/
├── src/                    # Main source code
│   ├── backend/           # Backend API and services
│   │   ├── __init__.py
│   │   ├── app.py         # Flask application factory
│   │   ├── config.py      # Configuration management
│   │   ├── models.py      # Database models
│   │   ├── routes.py      # API routes
│   │   └── tasks.py       # Celery background tasks
│   ├── frontend/          # React.js web application
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── utils/         # Utility functions
│   │   ├── styles/        # CSS and styling
│   │   ├── App.js         # Main App component
│   │   └── index.js       # Application entry point
│   ├── core/              # Core processing algorithms
│   │   ├── __init__.py
│   │   ├── processor.py   # Main processing engine
│   │   └── SpectralCarbonPoolEstimator.py  # Original estimator
│   ├── models/            # Machine learning models
│   │   ├── __init__.py
│   │   ├── species_classifier.py  # Species classification
│   │   └── carbon_estimator.py    # Carbon estimation
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py     # Helper functions
│   └── main.py            # Application entry point
├── tests/                 # Test suites
│   ├── __init__.py
│   └── test_core.py       # Core functionality tests
├── config/                # Configuration files
│   ├── development.json   # Development configuration
│   └── production.json    # Production configuration
├── scripts/               # Build and deployment scripts
│   ├── setup.sh          # Development setup
│   ├── run-tests.sh      # Test runner
│   └── deploy.sh         # Deployment script
├── data/                  # Data directories
│   ├── uploads/          # Uploaded files
│   └── results/          # Processing results
├── docker/                # Docker configuration
├── docs/                  # Documentation
│   ├── PRD_Hypersequester.md
│   ├── Implementation_Plan_Hypersequester.md
│   └── DEVELOPMENT_GUIDE.md
├── logs/                  # Application logs
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker services
├── requirements.txt      # Python dependencies
├── package.json          # Node.js dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # Project overview
```

## Development Workflow

### 1. Feature Development

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   ./scripts/run-tests.sh
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create a pull request**

### 2. Code Standards

**Python:**
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings for all functions and classes
- Maximum line length: 88 characters (Black formatter)

**JavaScript:**
- Use ES6+ features
- Follow Airbnb style guide
- Use meaningful variable names
- Add JSDoc comments for complex functions

**Git Commits:**
- Use conventional commit format
- Keep commits atomic and focused
- Write clear commit messages

### 3. Database Migrations

When making database schema changes:

```bash
# Create migration
python src/manage.py db migrate -m "Description of changes"

# Apply migration
python src/manage.py db upgrade

# Rollback if needed
python src/manage.py db downgrade
```

## Testing

### Running Tests

```bash
# Run all tests
./scripts/run-tests.sh

# Run specific test files
pytest tests/test_core.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run frontend tests
npm test
```

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows
- **Performance Tests**: Test processing performance

### Writing Tests

```python
# Example test
def test_carbon_estimation():
    estimator = CarbonEstimator()
    sample_data = create_sample_data()
    
    results = estimator.train(sample_data)
    
    assert results['validation_r2'] > 0.8
    assert 'total_carbon' in results
```

## Deployment

### Development Deployment

```bash
./scripts/deploy.sh development
```

### Production Deployment

```bash
./scripts/deploy.sh production v1.0.0
```

### Environment Configuration

Each environment has its own configuration file in the `config/` directory:

- `development.json`: Local development
- `staging.json`: Staging environment
- `production.json`: Production environment

### Monitoring

- **Application Logs**: `docker-compose logs -f app`
- **Database Logs**: `docker-compose logs -f postgres`
- **Worker Logs**: `docker-compose logs -f celery-worker`

## Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add changelog entry
4. Request review from maintainers
5. Address review feedback
6. Merge after approval

### Code Review Guidelines

- Check for code quality and standards
- Verify test coverage
- Review security implications
- Ensure documentation is updated
- Test the changes locally

### Issue Reporting

When reporting issues:

1. Use the issue template
2. Provide clear reproduction steps
3. Include environment information
4. Add relevant logs or screenshots
5. Label appropriately

For more detailed information, see the individual documentation files in the `docs/` directory.
