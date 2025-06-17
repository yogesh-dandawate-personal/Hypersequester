# Forest Carbon Assessment Platform - Deployment Guide

A comprehensive web-based platform for hyperspectral carbon assessment with role-based access control, spatial mapping, and advanced data visualization.

## 🌟 Features

### User Interface
- **Interactive Maps**: Leaflet-based mapping with multiple base layers
- **Role-Based Access Control**: 5 different user roles with specific permissions
- **Responsive Design**: Mobile and desktop optimized
- **Real-time Data Visualization**: Charts and statistics
- **Property Management**: Create, view, and manage forest properties
- **Export Capabilities**: CSV, GeoJSON, and report generation

### Backend API
- **RESTful API**: Complete CRUD operations
- **JWT Authentication**: Secure token-based authentication
- **Database Integration**: SQLite with SQLAlchemy ORM
- **File Processing**: Integration with hyperspectral analysis engine
- **Geospatial Support**: GeoJSON export and polygon handling

### Data Processing
- **Hyperspectral Analysis**: Research-based spectral wavelengths
- **Carbon Pool Estimation**: Biochemical composition analysis
- **Forest Classification**: Automated species identification
- **Metadata Management**: Comprehensive data provenance

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
python --version

# Required packages
pip install flask flask-cors flask-sqlalchemy werkzeug pyjwt pandas numpy geojson
pip install spectral rasterio shapely pyproj  # Optional for full functionality
```

### Installation

1. **Clone or Download Files**
   ```bash
   mkdir carbon_assessment_platform
   cd carbon_assessment_platform
   ```

2. **Save the Files**
   - Save the HTML file as `index.html`
   - Save the Python backend as `app.py`
   - Save the spectral estimator as `spectral_carbon_estimator.py`

3. **Start the Backend**
   ```bash
   python app.py
   ```
   This will:
   - Initialize the SQLite database
   - Create sample users and properties
   - Start the API server on `http://localhost:5000`

4. **Open the Frontend**
   - Open `index.html` in a web browser
   - Or serve with a simple HTTP server:
   ```bash
   python -m http.server 8080
   # Then visit http://localhost:8080
   ```

## 👥 User Roles & Permissions

### Administrator
- **Access**: All features and data
- **Permissions**: Create/edit/delete users, properties, assessments
- **Views**: Dashboard, Map, Properties, Reports, User Management, Settings
- **Use Case**: System administrators, platform managers

**Demo Login**: `admin` / `admin123`

### Forest Manager
- **Access**: Properties they own or manage
- **Permissions**: Create/edit properties and assessments
- **Views**: Dashboard, Map, Properties, Reports
- **Use Case**: Forest service personnel, land managers

**Demo Login**: `forest_manager` / `manager123`

### Scientist/Researcher
- **Access**: Public data and research-approved properties
- **Permissions**: Read-only access, data export
- **Views**: Dashboard, Map, Properties, Reports
- **Use Case**: University researchers, environmental scientists

**Demo Login**: `scientist` / `science123`

### Auditor
- **Access**: Properties under audit scope
- **Permissions**: Read-only with audit trail access
- **Views**: Dashboard, Map, Properties, Reports
- **Use Case**: Carbon credit auditors, compliance officers

**Demo Login**: `auditor` / `audit123`

### Public Viewer
- **Access**: Public properties only
- **Permissions**: Limited read-only access
- **Views**: Dashboard, Map (limited)
- **Use Case**: General public, educational use

**Demo Login**: `public_user` / `public123`

## 🗺️ Map Features

### Interactive Layers
- **Carbon Density**: Heat map of carbon storage
- **Biomass Distribution**: Forest biomass visualization
- **Forest Types**: Species classification overlay
- **Property Boundaries**: Legal boundaries and ownership

### Base Maps
- **Satellite**: High-resolution satellite imagery
- **Terrain**: Topographic relief maps
- **Hybrid**: Combined satellite and road overlay

### Controls
- **Layer Toggle**: Show/hide data layers
- **Search**: Find properties by name or owner
- **Export**: Download visible data as CSV or GeoJSON

## 📊 Data Management

### Property Creation
```json
{
  "name": "Example Forest",
  "owner_name": "Forest Owner",
  "polygon_coordinates": [
    [-122.5, 45.5], [-122.4, 45.5],
    [-122.4, 45.6], [-122.5, 45.6],
    [-122.5, 45.5]
  ],
  "area_hectares": 100.5,
  "is_public": false
}
```

### Assessment Processing
```json
{
  "property_id": 1,
  "capture_datetime": "2024-06-15T10:30:00Z",
  "sensor_info": "AVIRIS-NG Hyperspectral",
  "flight_altitude": 1000,
  "weather_conditions": "Clear skies"
}
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Properties
- `GET /api/properties` - List accessible properties
- `GET /api/properties/{id}` - Get property details
- `POST /api/properties` - Create new property
- `PUT /api/properties/{id}` - Update property

### Assessments
- `POST /api/assessments` - Create new assessment
- `GET /api/assessments/{id}` - Get assessment details

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

### Export
- `GET /api/export/csv` - Export data as CSV
- `GET /api/map/geojson` - Export map data as GeoJSON

### Admin
- `GET /api/users` - List all users (admin only)
- `POST /api/users` - Create new user (admin only)

## 🔒 Security Features

### Authentication
- JWT token-based authentication
- Password hashing with Werkzeug
- Token expiration (24 hours)
- Role-based route protection

### Authorization
- Property-level access control
- Action-based permissions (read/write/admin)
- Data filtering based on user role
- Audit trail for sensitive operations

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration

## 📁 File Structure

```
carbon_assessment_platform/
├── index.html                    # Frontend application
├── app.py                       # Backend API server
├── spectral_carbon_estimator.py # Hyperspectral processing
├── carbon_assessment.db        # SQLite database (auto-created)
├── uploads/                     # Hyperspectral data files
├── exports/                     # Generated reports and exports
└── static/                      # Static assets (optional)
    ├── css/
    ├── js/
    └── images/
```

## 🔄 Workflow Examples

### Adding a New Property
1. Login as Administrator or Forest Manager
2. Navigate to Properties view
3. Click "Add New Property"
4. Fill in property details and boundary coordinates
5. Set access permissions
6. Save property

### Processing Hyperspectral Data
1. Upload hyperspectral image file
2. Create new assessment for target property
3. Configure capture metadata
4. Run automated analysis
5. Review results and quality metrics
6. Generate reports

### Viewing Assessment Results
1. Login with appropriate role
2. Navigate to Map or Properties view
3. Select property of interest
4. View latest assessment data
5. Compare historical trends
6. Export data if permitted

## 🛠️ Customization

### Adding New Spectral Indices
Modify `spectral_carbon_estimator.py`:
```python
def calculate_custom_index(self, band_reflectances):
    # Add your custom vegetation index
    custom_index = (band_reflectances['nir'] - band_reflectances['red']) / \
                   (band_reflectances['nir'] + band_reflectances['red'])
    return custom_index
```

### Custom User Roles
Modify `ROLE_PERMISSIONS` in `app.py`:
```python
ROLE_PERMISSIONS['custom_role'] = {
    'views': ['dashboard', 'map'],
    'actions': ['read'],
    'layers': ['carbon'],
    'data_access': 'custom_logic'
}
```

### Additional Map Layers
Add to the frontend JavaScript:
```javascript
const customLayer = L.tileLayer('https://your-tile-server/{z}/{x}/{y}.png');
map.addLayer(customLayer);
```

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Reset database
rm carbon_assessment.db
python app.py  # Will recreate with sample data
```

**Authentication Issues**
```bash
# Check JWT token in browser developer tools
# Verify token hasn't expired (24-hour limit)
```

**Map Not Loading**
```bash
# Check internet connection for tile servers
# Verify Leaflet CDN is accessible
```

**File Upload Errors**
```bash
# Check file permissions in uploads/ directory
# Verify file format is supported
```

### Performance Optimization

**Large Datasets**
- Implement pagination for property lists
- Use database indexing for spatial queries
- Consider PostGIS for advanced spatial operations

**Map Performance**
- Cluster markers for large numbers of properties
- Implement level-of-detail for data layers
- Use vector tiles for complex geometries

## 📈 Scaling Considerations

### Database Migration
For production deployment, consider:
- PostgreSQL with PostGIS extension
- Database connection pooling
- Read replicas for heavy query loads

### File Storage
- Cloud storage (AWS S3, Google Cloud Storage)
- CDN for static assets
- Distributed file processing

### Authentication
- Integration with LDAP/Active Directory
- OAuth2 providers (Google, Microsoft)
- Multi-factor authentication

## 🚀 Production Deployment

### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Using systemd (Linux)
```ini
[Unit]
Description=Carbon Assessment API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/carbon-assessment
ExecStart=/opt/carbon-assessment/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /opt/carbon-assessment/static;
    }
}
```

## 📞 Support

For technical support or questions:
- Check the troubleshooting section above
- Review API documentation
- Examine browser developer console for errors
- Verify user permissions and roles

## 📄 License

This platform is designed for environmental monitoring and carbon assessment applications. Please ensure compliance with local regulations regarding forest data and carbon credit systems.

---

*Last updated: December 2024*
*Version: 2.0*
