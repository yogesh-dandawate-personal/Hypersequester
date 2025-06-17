#!/usr/bin/env python3
"""
Spectral Carbon Pool Estimator
Implements research-based spectral wavelengths for accurate carbon assessment
Based on optimized bands: red edge, SWIR biochemical, and structural indicators
"""

import numpy as np
import pandas as pd
from scipy import ndimage
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime, timezone
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import warnings
warnings.filterwarnings('ignore')

try:
    import spectral
    HAS_SPECTRAL = True
except ImportError:
    HAS_SPECTRAL = False

try:
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

try:
    from shapely.geometry import Polygon, Point
    from shapely.ops import transform
    import pyproj
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False

class MetadataManager:
    """
    Handles metadata for hyperspectral carbon assessments including
    landowner info, geocoding, timestamps, and KML generation
    """
    
    def __init__(self):
        self.metadata = {
            'capture_info': {},
            'geographic_info': {},
            'landowner_info': {},
            'processing_info': {},
            'quality_metrics': {},
            'carbon_assessment': {}
        }
    
    def set_capture_info(self, capture_datetime=None, sensor_info=None, 
                        flight_altitude=None, weather_conditions=None):
        """Set capture-related metadata"""
        if capture_datetime is None:
            capture_datetime = datetime.now(timezone.utc)
        elif isinstance(capture_datetime, str):
            capture_datetime = datetime.fromisoformat(capture_datetime)
        
        self.metadata['capture_info'] = {
            'datetime_utc': capture_datetime.isoformat(),
            'date': capture_datetime.strftime('%Y-%m-%d'),
            'time': capture_datetime.strftime('%H:%M:%S UTC'),
            'sensor_info': sensor_info or "Unknown Hyperspectral Sensor",
            'flight_altitude_m': flight_altitude,
            'weather_conditions': weather_conditions,
            'spectral_range_nm': None,  # Will be filled during processing
            'spatial_resolution_m': None  # Will be filled during processing
        }
    
    def set_geographic_info(self, polygon_coords=None, crs='EPSG:4326', 
                           location_name=None, country=None, state_province=None):
        """Set geographic information"""
        self.metadata['geographic_info'] = {
            'polygon_coordinates': polygon_coords,  # List of [lon, lat] pairs
            'coordinate_system': crs,
            'location_name': location_name,
            'country': country,
            'state_province': state_province,
            'area_hectares': None,  # Will be calculated
            'centroid_lat': None,   # Will be calculated
            'centroid_lon': None    # Will be calculated
        }
        
        if polygon_coords and len(polygon_coords) >= 3:
            self._calculate_area_and_centroid(polygon_coords)
    
    def set_landowner_info(self, owner_name=None, owner_type=None, 
                          contact_info=None, property_id=None, 
                          land_use_type=None, management_notes=None):
        """Set landowner and property information"""
        self.metadata['landowner_info'] = {
            'owner_name': owner_name,
            'owner_type': owner_type,  # e.g., 'Private', 'Government', 'NGO', 'Corporate'
            'contact_info': contact_info,
            'property_id': property_id,
            'land_use_type': land_use_type,  # e.g., 'Forestry', 'Conservation', 'Mixed'
            'management_notes': management_notes,
            'certification_status': None,  # e.g., 'FSC Certified', 'Sustainable'
            'carbon_credits_eligible': None
        }
    
    def set_processing_info(self, processing_datetime=None, software_version=None,
                           processing_parameters=None, quality_flags=None):
        """Set processing-related metadata"""
        if processing_datetime is None:
            processing_datetime = datetime.now(timezone.utc)
        
        self.metadata['processing_info'] = {
            'processing_datetime_utc': processing_datetime.isoformat(),
            'software_version': software_version or "SpectralCarbonEstimator v1.0",
            'processing_parameters': processing_parameters or {},
            'quality_flags': quality_flags or [],
            'algorithms_used': [
                'Red Edge Position Analysis',
                'Biochemical Component Estimation',
                'Forest Type Classification',
                'Carbon Pool Calculation'
            ]
        }
    
    def _calculate_area_and_centroid(self, polygon_coords):
        """Calculate area in hectares and centroid coordinates"""
        if HAS_SHAPELY:
            try:
                # Create polygon
                polygon = Polygon(polygon_coords)
                
                # Calculate centroid
                centroid = polygon.centroid
                self.metadata['geographic_info']['centroid_lon'] = centroid.x
                self.metadata['geographic_info']['centroid_lat'] = centroid.y
                
                # Calculate area (approximate for lat/lon)
                # Convert to UTM for accurate area calculation
                if polygon.bounds:
                    lon_center = (polygon.bounds[0] + polygon.bounds[2]) / 2
                    lat_center = (polygon.bounds[1] + polygon.bounds[3]) / 2
                    
                    # Estimate UTM zone
                    utm_zone = int((lon_center + 180) / 6) + 1
                    utm_crs = f'EPSG:{32600 + utm_zone if lat_center >= 0 else 32700 + utm_zone}'
                    
                    # Transform to UTM
                    transformer = pyproj.Transformer.from_crs('EPSG:4326', utm_crs, always_xy=True)
                    utm_polygon = transform(transformer.transform, polygon)
                    
                    # Calculate area in square meters, convert to hectares
                    area_m2 = utm_polygon.area
                    area_hectares = area_m2 / 10000
                    self.metadata['geographic_info']['area_hectares'] = round(area_hectares, 2)
                    
            except Exception as e:
                print(f"Warning: Could not calculate area and centroid: {e}")
                # Fallback: simple centroid calculation
                lons = [coord[0] for coord in polygon_coords]
                lats = [coord[1] for coord in polygon_coords]
                self.metadata['geographic_info']['centroid_lon'] = sum(lons) / len(lons)
                self.metadata['geographic_info']['centroid_lat'] = sum(lats) / len(lats)
    
    def update_carbon_assessment(self, carbon_results):
        """Update metadata with carbon assessment results"""
        self.metadata['carbon_assessment'] = {
            'total_carbon_tonnes': float(carbon_results.get('total_carbon_kg', 0)) / 1000,
            'total_co2_equivalent_tonnes': float(carbon_results.get('total_co2_tonnes', 0)),
            'carbon_density_tonnes_per_hectare': None,
            'forest_types_detected': [],
            'assessment_confidence': None,
            'carbon_sequestration_potential': None
        }
        
        # Calculate carbon density per hectare
        if self.metadata['geographic_info']['area_hectares']:
            area_ha = self.metadata['geographic_info']['area_hectares']
            self.metadata['carbon_assessment']['carbon_density_tonnes_per_hectare'] = \
                round(self.metadata['carbon_assessment']['total_co2_equivalent_tonnes'] / area_ha, 2)
    
    def generate_kml(self, output_path, include_carbon_data=True):
        """Generate KML file with polygon and metadata"""
        
        # Create KML structure
        kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        document = ET.SubElement(kml, 'Document')
        
        # Document name and description
        name = ET.SubElement(document, 'name')
        name.text = f"Carbon Assessment - {self.metadata['geographic_info'].get('location_name', 'Unknown Location')}"
        
        description = ET.SubElement(document, 'description')
        description.text = self._generate_kml_description()
        
        # Add styles for different forest types
        self._add_kml_styles(document)
        
        # Add polygon placemark
        placemark = ET.SubElement(document, 'Placemark')
        placemark_name = ET.SubElement(placemark, 'name')
        placemark_name.text = "Study Area Boundary"
        
        # Extended data with metadata
        extended_data = ET.SubElement(placemark, 'ExtendedData')
        self._add_extended_data(extended_data)
        
        # Style reference
        style_url = ET.SubElement(placemark, 'styleUrl')
        style_url.text = "#study_area_style"
        
        # Polygon geometry
        if self.metadata['geographic_info']['polygon_coordinates']:
            polygon = ET.SubElement(placemark, 'Polygon')
            outer_boundary = ET.SubElement(polygon, 'outerBoundaryIs')
            linear_ring = ET.SubElement(outer_boundary, 'LinearRing')
            coordinates = ET.SubElement(linear_ring, 'coordinates')
            
            # Format coordinates as lon,lat,alt
            coord_strings = []
            for coord in self.metadata['geographic_info']['polygon_coordinates']:
                if len(coord) >= 2:
                    coord_strings.append(f"{coord[0]},{coord[1]},0")
            
            # Close polygon by repeating first coordinate
            if coord_strings and coord_strings[0] != coord_strings[-1]:
                coord_strings.append(coord_strings[0])
            
            coordinates.text = ' '.join(coord_strings)
        
        # Write KML file
        self._write_kml_file(kml, output_path)
        print(f"KML file generated: {output_path}")
        
        return output_path
    
    def _generate_kml_description(self):
        """Generate HTML description for KML"""
        desc = "<![CDATA["
        desc += "<h3>Hyperspectral Carbon Assessment</h3>"
        
        # Capture info
        if self.metadata['capture_info']:
            desc += "<h4>Capture Information</h4>"
            desc += f"<p><b>Date:</b> {self.metadata['capture_info'].get('date', 'Unknown')}<br/>"
            desc += f"<b>Time:</b> {self.metadata['capture_info'].get('time', 'Unknown')}<br/>"
            desc += f"<b>Sensor:</b> {self.metadata['capture_info'].get('sensor_info', 'Unknown')}</p>"
        
        # Landowner info
        if self.metadata['landowner_info'].get('owner_name'):
            desc += "<h4>Property Information</h4>"
            desc += f"<p><b>Owner:</b> {self.metadata['landowner_info']['owner_name']}<br/>"
            if self.metadata['landowner_info'].get('property_id'):
                desc += f"<b>Property ID:</b> {self.metadata['landowner_info']['property_id']}<br/>"
            if self.metadata['landowner_info'].get('land_use_type'):
                desc += f"<b>Land Use:</b> {self.metadata['landowner_info']['land_use_type']}</p>"
        
        # Geographic info
        if self.metadata['geographic_info']:
            desc += "<h4>Geographic Information</h4>"
            desc += f"<p><b>Location:</b> {self.metadata['geographic_info'].get('location_name', 'Unknown')}<br/>"
            if self.metadata['geographic_info'].get('area_hectares'):
                desc += f"<b>Area:</b> {self.metadata['geographic_info']['area_hectares']} hectares<br/>"
            if self.metadata['geographic_info'].get('country'):
                desc += f"<b>Country:</b> {self.metadata['geographic_info']['country']}</p>"
        
        # Carbon assessment results
        if self.metadata['carbon_assessment']:
            desc += "<h4>Carbon Assessment Results</h4>"
            desc += f"<p><b>Total Carbon:</b> {self.metadata['carbon_assessment'].get('total_carbon_tonnes', 0):.1f} tonnes<br/>"
            desc += f"<b>CO₂ Equivalent:</b> {self.metadata['carbon_assessment'].get('total_co2_equivalent_tonnes', 0):.1f} tonnes<br/>"
            if self.metadata['carbon_assessment'].get('carbon_density_tonnes_per_hectare'):
                desc += f"<b>Carbon Density:</b> {self.metadata['carbon_assessment']['carbon_density_tonnes_per_hectare']} tonnes CO₂/hectare</p>"
        
        desc += "]]>"
        return desc
    
    def _add_kml_styles(self, document):
        """Add KML styles for visualization"""
        style = ET.SubElement(document, 'Style', id="study_area_style")
        line_style = ET.SubElement(style, 'LineStyle')
        line_color = ET.SubElement(line_style, 'color')
        line_color.text = "ff0000ff"  # Red border
        line_width = ET.SubElement(line_style, 'width')
        line_width.text = "3"
        
        poly_style = ET.SubElement(style, 'PolyStyle')
        poly_color = ET.SubElement(poly_style, 'color')
        poly_color.text = "4000ff00"  # Semi-transparent green fill
    
    def _add_extended_data(self, extended_data):
        """Add extended data to KML placemark"""
        # Add key metadata as extended data
        data_items = [
            ('capture_date', self.metadata['capture_info'].get('date')),
            ('sensor_info', self.metadata['capture_info'].get('sensor_info')),
            ('owner_name', self.metadata['landowner_info'].get('owner_name')),
            ('property_id', self.metadata['landowner_info'].get('property_id')),
            ('total_carbon_tonnes', self.metadata['carbon_assessment'].get('total_carbon_tonnes')),
            ('co2_equivalent_tonnes', self.metadata['carbon_assessment'].get('total_co2_equivalent_tonnes')),
            ('area_hectares', self.metadata['geographic_info'].get('area_hectares'))
        ]
        
        for name, value in data_items:
            if value is not None:
                data = ET.SubElement(extended_data, 'Data', name=name)
                data_value = ET.SubElement(data, 'value')
                data_value.text = str(value)
    
    def _write_kml_file(self, kml_element, output_path):
        """Write KML to file with proper formatting"""
        rough_string = ET.tostring(kml_element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(reparsed.toprettyxml(indent="  "))
    
    def export_metadata_json(self, output_path):
        """Export complete metadata as JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False, default=str)
        print(f"Metadata JSON exported: {output_path}")
        return output_path
    
    def export_carbon_report(self, output_path, carbon_pools=None):
        """Export detailed carbon assessment report"""
        report = {
            'report_header': {
                'title': 'Hyperspectral Carbon Pool Assessment Report',
                'generated_datetime': datetime.now(timezone.utc).isoformat(),
                'report_version': '1.0'
            },
            'metadata': self.metadata,
            'executive_summary': self._generate_executive_summary(),
            'detailed_results': carbon_pools if carbon_pools else {},
            'methodology': {
                'spectral_bands_used': [
                    'Red Edge (674-730nm): Biomass and LAI estimation',
                    'SWIR Lignin (1680nm): Wood composition analysis', 
                    'SWIR Cellulose (2100nm, 2300nm): Biochemical content',
                    'Water Bands (1450nm, 1940nm): Moisture content'
                ],
                'carbon_conversion_factors': {
                    'lignin_carbon_fraction': 0.63,
                    'cellulose_carbon_fraction': 0.44,
                    'dry_matter_fraction': 0.85,
                    'co2_conversion_factor': 3.67
                }
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"Carbon assessment report exported: {output_path}")
        return output_path
    
    def _generate_executive_summary(self):
        """Generate executive summary for carbon report"""
        summary = {
            'assessment_overview': f"Hyperspectral carbon assessment of {self.metadata['geographic_info'].get('area_hectares', 'unknown')} hectares",
            'key_findings': {},
            'recommendations': []
        }
        
        if self.metadata['carbon_assessment']:
            total_carbon = self.metadata['carbon_assessment'].get('total_co2_equivalent_tonnes', 0)
            carbon_density = self.metadata['carbon_assessment'].get('carbon_density_tonnes_per_hectare', 0)
            
            summary['key_findings'] = {
                'total_carbon_stored': f"{total_carbon:.1f} tonnes CO₂ equivalent",
                'carbon_density': f"{carbon_density:.1f} tonnes CO₂ per hectare",
                'assessment_date': self.metadata['capture_info'].get('date', 'Unknown')
            }
            
            # Generate recommendations based on carbon density
            if carbon_density > 100:
                summary['recommendations'].append("High carbon density forest - prioritize for conservation")
            elif carbon_density > 50:
                summary['recommendations'].append("Moderate carbon density - sustainable management recommended")
            else:
                summary['recommendations'].append("Low carbon density - consider reforestation opportunities")
        
        return summary

class SpectralCarbonEstimator:
    """
    Advanced carbon pool estimator using research-optimized spectral bands
    with comprehensive metadata management and geographic information
    """
    
    def __init__(self, pixel_size=1.0):
        self.pixel_size = pixel_size
        self.key_wavelengths = self._define_key_wavelengths()
        self.vegetation_indices = {}
        self.biochemical_maps = {}
        self.carbon_factors = self._define_carbon_factors()
        self.metadata_manager = MetadataManager()
        
    def setup_metadata(self, capture_datetime=None, sensor_info=None, 
                      polygon_coords=None, location_name=None,
                      owner_name=None, owner_type=None, property_id=None,
                      contact_info=None, land_use_type=None, country=None,
                      state_province=None, flight_altitude=None,
                      weather_conditions=None, management_notes=None):
        """
        Setup comprehensive metadata for the carbon assessment
        
        Parameters:
        -----------
        capture_datetime : str or datetime
            Date and time of image capture (ISO format or datetime object)
        sensor_info : str
            Information about the hyperspectral sensor used
        polygon_coords : list
            List of [longitude, latitude] coordinate pairs defining study area boundary
        location_name : str
            Descriptive name of the location
        owner_name : str
            Name of the landowner or managing entity
        owner_type : str
            Type of ownership ('Private', 'Government', 'NGO', 'Corporate')
        property_id : str
            Unique identifier for the property
        contact_info : str
            Contact information for the landowner
        land_use_type : str
            Type of land use ('Forestry', 'Conservation', 'Mixed', etc.)
        country : str
            Country where the study area is located
        state_province : str
            State or province
        flight_altitude : float
            Flight altitude in meters (for airborne sensors)
        weather_conditions : str
            Weather conditions during capture
        management_notes : str
            Notes about forest management practices
        
        Example:
        --------
        estimator.setup_metadata(
            capture_datetime='2024-06-15T10:30:00Z',
            sensor_info='AVIRIS-NG Hyperspectral Imager',
            polygon_coords=[[-122.5, 45.5], [-122.4, 45.5], [-122.4, 45.6], [-122.5, 45.6]],
            location_name='Pacific Northwest Forest Reserve',
            owner_name='Oregon State Forest Service',
            owner_type='Government',
            property_id='OR-FOREST-001',
            country='United States',
            state_province='Oregon',
            land_use_type='Conservation'
        )
        """
        
        # Set capture information
        self.metadata_manager.set_capture_info(
            capture_datetime=capture_datetime,
            sensor_info=sensor_info,
            flight_altitude=flight_altitude,
            weather_conditions=weather_conditions
        )
        
        # Set geographic information
        self.metadata_manager.set_geographic_info(
            polygon_coords=polygon_coords,
            location_name=location_name,
            country=country,
            state_province=state_province
        )
        
        # Set landowner information
        self.metadata_manager.set_landowner_info(
            owner_name=owner_name,
            owner_type=owner_type,
            contact_info=contact_info,
            property_id=property_id,
            land_use_type=land_use_type,
            management_notes=management_notes
        )
        
        print("Metadata setup completed successfully!")
        return self.metadata_manager.metadata
        
    def _define_key_wavelengths(self):
        """Define research-based key wavelengths for carbon estimation"""
        return {
            # Visible region for vegetation health
            'blue_chlorophyll': 430,
            'green_peak': 550, 
            'red_chlorophyll': 660,
            
            # Red edge region (MOST IMPORTANT for biomass)
            'red_edge_1': 674,  # Optimal for LAI with 712nm
            'red_edge_2': 700,  # Start of red edge transition
            'red_edge_3': 710,  # Critical for chlorophyll content
            'red_edge_4': 712,  # Optimal for LAI with 674nm
            'red_edge_5': 720,  # Peak red edge
            'red_edge_6': 730,  # End of red edge transition
            
            # Near-infrared for structure
            'nir_1': 780,       # Vegetation structure
            'nir_2': 925,       # Chlorophyll indices reference
            'nir_3': 970,       # LAI calculation reference
            
            # SWIR for biochemical composition
            'water_1': 1450,    # Primary water absorption
            'water_2': 1490,    # Leaf mass per area
            'lignin': 1680,     # Lignin absorption
            'lai_ref': 1725,    # LAI calculation
            'water_3': 1940,    # Secondary water absorption
            'cellulose_1': 2100, # Cellulose absorption
            'biomass_1': 2160,  # Biomass estimation
            'protein': 2180,    # Protein content
            'lma_ref': 2260,    # Leaf mass per area reference
            'cellulose_2': 2300, # Strong cellulose absorption
        }
    
    def _define_carbon_factors(self):
        """Define carbon conversion factors and biochemical relationships"""
        return {
            'carbon_fraction': 0.47,        # Carbon content in dry wood
            'dry_matter_fraction': 0.85,    # Dry matter content
            'co2_conversion': 3.67,         # CO2 to carbon conversion
            'wood_densities': {
                'conifer': 450,    # kg/m³ (high lignin)
                'deciduous': 650,  # kg/m³ (high cellulose)
                'mixed': 550,      # kg/m³ (average)
                'default': 600
            },
            'lignin_carbon': 0.63,          # Carbon content in lignin
            'cellulose_carbon': 0.44,       # Carbon content in cellulose
            'hemicellulose_carbon': 0.45,   # Carbon content in hemicellulose
        }
    
    def load_hyperspectral_image(self, file_path, wavelengths=None):
        """
        Load hyperspectral image with wavelength information
        """
        print(f"Loading hyperspectral image: {file_path}")
        
        if HAS_SPECTRAL and file_path.endswith('.hdr'):
            img = spectral.open_image(file_path)
            data = img.load()
            if hasattr(img, 'metadata') and 'wavelength' in img.metadata:
                wavelengths = np.array([float(w) for w in img.metadata['wavelength']])
            else:
                wavelengths = np.linspace(400, 2500, data.shape[2])
            return np.array(data), wavelengths
            
        elif HAS_RASTERIO:
            with rasterio.open(file_path) as dataset:
                data = dataset.read()
                data = np.transpose(data, (1, 2, 0))
                if wavelengths is None:
                    wavelengths = np.linspace(400, 2500, data.shape[2])
                return data, wavelengths
        else:
            # Generate synthetic data for demonstration
            print("Generating synthetic hyperspectral data...")
            return self._generate_synthetic_data()
    
    def _generate_synthetic_data(self, height=200, width=200):
        """Generate realistic synthetic hyperspectral data"""
        # Create wavelength array from 400-2500nm
        wavelengths = np.linspace(400, 2500, 224)  # Typical hyperspectral bands
        
        # Initialize data
        data = np.zeros((height, width, len(wavelengths)))
        
        # Create forest patches with different species
        np.random.seed(42)
        
        # Define forest regions
        y, x = np.ogrid[:height, :width]
        center_y, center_x = height // 2, width // 2
        
        # Coniferous forest (high lignin)
        conifer_mask = ((y - center_y + 30)**2 + (x - center_x - 40)**2) < 1200
        # Deciduous forest (high cellulose)
        deciduous_mask = ((y - center_y - 30)**2 + (x - center_x + 40)**2) < 1000
        # Mixed forest
        mixed_mask = ((y - center_y)**2 + (x - center_x)**2) < 800
        
        # Generate spectra for each forest type
        for i in range(height):
            for j in range(width):
                if conifer_mask[i, j]:
                    spectrum = self._generate_conifer_spectrum(wavelengths)
                elif deciduous_mask[i, j]:
                    spectrum = self._generate_deciduous_spectrum(wavelengths)
                elif mixed_mask[i, j]:
                    spectrum = self._generate_mixed_spectrum(wavelengths)
                else:
                    spectrum = self._generate_soil_spectrum(wavelengths)
                
                # Add realistic noise
                noise = np.random.normal(0, 0.02, len(wavelengths))
                data[i, j, :] = np.clip(spectrum + noise, 0, 1)
        
        return data, wavelengths
    
    def _generate_conifer_spectrum(self, wavelengths):
        """Generate coniferous forest spectrum (high lignin)"""
        spectrum = np.ones_like(wavelengths) * 0.05
        
        # Visible region - lower reflectance due to needle structure
        visible_mask = wavelengths < 700
        spectrum[visible_mask] += 0.1
        
        # Green peak (reduced compared to deciduous)
        green_mask = (wavelengths >= 520) & (wavelengths <= 600)
        spectrum[green_mask] += 0.15
        
        # Red edge (less pronounced)
        red_edge_mask = (wavelengths >= 700) & (wavelengths <= 750)
        spectrum[red_edge_mask] += 0.25
        
        # NIR plateau (lower than deciduous)
        nir_mask = (wavelengths >= 750) & (wavelengths <= 1300)
        spectrum[nir_mask] += 0.35
        
        # SWIR - strong lignin absorption at 1680nm
        lignin_mask = np.abs(wavelengths - 1680) < 30
        spectrum[lignin_mask] -= 0.25
        
        # Water bands
        for water_band in [1450, 1940]:
            water_mask = np.abs(wavelengths - water_band) < 40
            spectrum[water_mask] -= 0.2
        
        # Cellulose bands (weaker in conifers)
        for cellulose_band in [2100, 2300]:
            cellulose_mask = np.abs(wavelengths - cellulose_band) < 25
            spectrum[cellulose_mask] -= 0.1
        
        return np.clip(spectrum, 0.01, 0.8)
    
    def _generate_deciduous_spectrum(self, wavelengths):
        """Generate deciduous forest spectrum (high cellulose)"""
        spectrum = np.ones_like(wavelengths) * 0.05
        
        # Visible region - higher reflectance
        visible_mask = wavelengths < 700
        spectrum[visible_mask] += 0.15
        
        # Strong green peak
        green_mask = (wavelengths >= 520) & (wavelengths <= 600)
        spectrum[green_mask] += 0.25
        
        # Pronounced red edge
        red_edge_mask = (wavelengths >= 700) & (wavelengths <= 750)
        spectrum[red_edge_mask] += 0.4
        
        # High NIR plateau
        nir_mask = (wavelengths >= 750) & (wavelengths <= 1300)
        spectrum[nir_mask] += 0.45
        
        # Moderate lignin absorption
        lignin_mask = np.abs(wavelengths - 1680) < 30
        spectrum[lignin_mask] -= 0.15
        
        # Strong cellulose absorption
        for cellulose_band in [2100, 2300]:
            cellulose_mask = np.abs(wavelengths - cellulose_band) < 25
            spectrum[cellulose_mask] -= 0.25
        
        # Water bands
        for water_band in [1450, 1940]:
            water_mask = np.abs(wavelengths - water_band) < 40
            spectrum[water_mask] -= 0.2
        
        return np.clip(spectrum, 0.01, 0.85)
    
    def _generate_mixed_spectrum(self, wavelengths):
        """Generate mixed forest spectrum"""
        conifer = self._generate_conifer_spectrum(wavelengths)
        deciduous = self._generate_deciduous_spectrum(wavelengths)
        return (conifer + deciduous) / 2
    
    def _generate_soil_spectrum(self, wavelengths):
        """Generate soil/non-vegetation spectrum"""
        # Typical soil spectrum - gradually increasing with wavelength
        spectrum = 0.1 + 0.3 * (wavelengths - 400) / (2500 - 400)
        return np.clip(spectrum, 0.05, 0.4)
    
    def extract_key_bands(self, hsi_data, wavelengths):
        """Extract reflectance values at key wavelengths"""
        print("Extracting key spectral bands...")
        
        band_reflectances = {}
        
        for band_name, target_wavelength in self.key_wavelengths.items():
            # Find closest wavelength
            closest_idx = np.argmin(np.abs(wavelengths - target_wavelength))
            actual_wavelength = wavelengths[closest_idx]
            
            # Extract reflectance for this band
            band_reflectances[band_name] = hsi_data[:, :, closest_idx]
            
            print(f"{band_name}: Target {target_wavelength}nm, Actual {actual_wavelength:.1f}nm")
        
        return band_reflectances
    
    def calculate_vegetation_indices(self, band_reflectances):
        """Calculate research-based vegetation indices for carbon estimation"""
        print("Calculating vegetation indices...")
        
        indices = {}
        
        # Red edge indices for biomass and LAI
        indices['ndvi_red_edge'] = self._safe_division(
            band_reflectances['nir_1'] - band_reflectances['red_edge_1'],
            band_reflectances['nir_1'] + band_reflectances['red_edge_1']
        )
        
        # Optimized LAI index (674nm, 712nm combination)
        indices['lai_optimal'] = self._safe_division(
            band_reflectances['red_edge_4'] - band_reflectances['red_edge_1'],
            band_reflectances['red_edge_4'] + band_reflectances['red_edge_1']
        )
        
        # Chlorophyll content index (925nm, 710nm)
        indices['chlorophyll_content'] = self._safe_division(
            band_reflectances['nir_2'] - band_reflectances['red_edge_3'],
            band_reflectances['nir_2'] + band_reflectances['red_edge_3']
        )
        
        # Leaf Mass per Area (2260nm, 1490nm)
        indices['leaf_mass_area'] = self._safe_division(
            band_reflectances['lma_ref'] - band_reflectances['water_2'],
            band_reflectances['lma_ref'] + band_reflectances['water_2']
        )
        
        # LAI difference index (1725nm - 970nm)
        indices['lai_difference'] = band_reflectances['lai_ref'] - band_reflectances['nir_3']
        
        # Biomass index (2160nm, 1540nm approximated by 1490nm)
        indices['biomass_index'] = self._safe_division(
            band_reflectances['biomass_1'] - band_reflectances['water_2'],
            band_reflectances['biomass_1'] + band_reflectances['water_2']
        )
        
        # Red Edge Position (REP) - critical for carbon assessment
        indices['red_edge_position'] = self._calculate_red_edge_position(band_reflectances)
        
        # Water content indices
        indices['water_index_1'] = 1 - band_reflectances['water_1']  # Higher absorption = higher water
        indices['water_index_2'] = 1 - band_reflectances['water_3']
        
        self.vegetation_indices = indices
        return indices
    
    def _calculate_red_edge_position(self, band_reflectances):
        """Calculate Red Edge Position - critical for biomass/carbon estimation"""
        # Simplified REP calculation using available bands
        r700 = band_reflectances['red_edge_2']
        r710 = band_reflectances['red_edge_3']
        r720 = band_reflectances['red_edge_5']
        r730 = band_reflectances['red_edge_6']
        
        # Linear interpolation to find inflection point
        rep = 700 + 20 * (r720 - r700) / (r730 - r700 + 1e-8)
        return np.clip(rep, 700, 730)
    
    def estimate_biochemical_content(self, band_reflectances):
        """Estimate lignin, cellulose, and other biochemical components"""
        print("Estimating biochemical content...")
        
        biochemical = {}
        
        # Lignin content (inverse relationship with 1680nm absorption)
        lignin_absorption = 1 - band_reflectances['lignin']
        biochemical['lignin_content'] = np.clip(lignin_absorption * 0.3, 0, 0.4)  # 0-40% lignin
        
        # Cellulose content (inverse relationship with 2100nm and 2300nm)
        cellulose_absorption_1 = 1 - band_reflectances['cellulose_1']
        cellulose_absorption_2 = 1 - band_reflectances['cellulose_2']
        cellulose_combined = (cellulose_absorption_1 + cellulose_absorption_2) / 2
        biochemical['cellulose_content'] = np.clip(cellulose_combined * 0.6, 0, 0.6)  # 0-60% cellulose
        
        # Hemicellulose (estimated from remaining fraction)
        biochemical['hemicellulose_content'] = np.clip(
            0.4 - biochemical['lignin_content'] - biochemical['cellulose_content'] * 0.5, 0, 0.3
        )
        
        # Water content (from water absorption bands)
        water_content = (band_reflectances['water_1'] + band_reflectances['water_3']) / 2
        biochemical['water_content'] = 1 - water_content
        
        # Protein content (from 2180nm band)
        protein_absorption = 1 - band_reflectances['protein']
        biochemical['protein_content'] = np.clip(protein_absorption * 0.15, 0, 0.15)  # 0-15% protein
        
        self.biochemical_maps = biochemical
        return biochemical
    
    def estimate_forest_structure(self, vegetation_indices):
        """Estimate forest structural parameters"""
        print("Estimating forest structure...")
        
        structure = {}
        
        # Leaf Area Index from optimized bands
        lai_base = vegetation_indices['lai_optimal'] * 8  # Scale to realistic LAI range
        lai_adjustment = vegetation_indices['lai_difference'] * 2
        structure['lai'] = np.clip(lai_base + lai_adjustment, 0, 10)
        
        # Canopy height estimation from red edge position and indices
        rep = vegetation_indices['red_edge_position']
        rep_normalized = (rep - 705) / 20  # Normalize REP to 0-1
        height_from_rep = rep_normalized * 30  # Scale to height range
        
        # Combine with other indices for height
        height_from_biomass = vegetation_indices['biomass_index'] * 25
        structure['canopy_height'] = np.clip(
            (height_from_rep + height_from_biomass) / 2, 0, 40
        )
        
        # Canopy cover from NDVI and chlorophyll
        structure['canopy_cover'] = np.clip(
            (vegetation_indices['ndvi_red_edge'] + vegetation_indices['chlorophyll_content']) / 2,
            0, 1
        )
        
        # Biomass density estimation
        structure['biomass_density'] = (
            vegetation_indices['biomass_index'] * 
            structure['lai'] * 
            structure['canopy_height'] * 0.1
        )
        
        return structure
    
    def classify_forest_type(self, biochemical_content):
        """Classify forest type based on biochemical composition"""
        print("Classifying forest types...")
        
        lignin = biochemical_content['lignin_content']
        cellulose = biochemical_content['cellulose_content']
        
        # Create forest type classification
        forest_type = np.zeros_like(lignin, dtype=int)
        
        # Coniferous: High lignin (>25%), moderate cellulose
        conifer_mask = (lignin > 0.25) & (cellulose < 0.45)
        forest_type[conifer_mask] = 1
        
        # Deciduous: High cellulose (>45%), moderate lignin
        deciduous_mask = (cellulose > 0.45) & (lignin < 0.25)
        forest_type[deciduous_mask] = 2
        
        # Mixed forest: Intermediate values
        mixed_mask = (lignin >= 0.15) & (lignin <= 0.25) & (cellulose >= 0.35) & (cellulose <= 0.45)
        forest_type[mixed_mask] = 3
        
        # Non-forest: Low lignin and cellulose
        # Remains 0 (default)
        
        return forest_type
    
    def calculate_carbon_pools(self, biochemical_content, forest_structure, forest_type):
        """Calculate carbon pools based on biochemical composition and structure"""
        print("Calculating carbon pools...")
        
        # Get basic parameters
        biomass_density = forest_structure['biomass_density']
        lai = forest_structure['lai']
        height = forest_structure['canopy_height']
        
        # Get biochemical fractions
        lignin_frac = biochemical_content['lignin_content']
        cellulose_frac = biochemical_content['cellulose_content']
        hemicellulose_frac = biochemical_content['hemicellulose_content']
        
        # Calculate carbon content based on biochemical composition
        carbon_from_lignin = lignin_frac * self.carbon_factors['lignin_carbon']
        carbon_from_cellulose = cellulose_frac * self.carbon_factors['cellulose_carbon']
        carbon_from_hemicellulose = hemicellulose_frac * self.carbon_factors['hemicellulose_carbon']
        
        total_carbon_fraction = carbon_from_lignin + carbon_from_cellulose + carbon_from_hemicellulose
        
        # Estimate total biomass from structural parameters
        # Volume estimation using height and LAI
        crown_volume = lai * height * self.pixel_size**2 * 0.1  # m³ per pixel
        
        # Wood density based on forest type
        wood_density = np.zeros_like(forest_type, dtype=float)
        wood_density[forest_type == 1] = self.carbon_factors['wood_densities']['conifer']      # Conifer
        wood_density[forest_type == 2] = self.carbon_factors['wood_densities']['deciduous']    # Deciduous
        wood_density[forest_type == 3] = self.carbon_factors['wood_densities']['mixed']        # Mixed
        wood_density[forest_type == 0] = 0  # Non-forest
        
        # Calculate biomass (kg per pixel)
        fresh_biomass = crown_volume * wood_density
        dry_biomass = fresh_biomass * self.carbon_factors['dry_matter_fraction']
        
        # Calculate carbon content using biochemical-specific carbon fractions
        carbon_content_kg = dry_biomass * total_carbon_fraction
        
        # Convert to CO2 equivalent
        co2_equivalent = carbon_content_kg * self.carbon_factors['co2_conversion'] / 1000  # tonnes CO2
        
        carbon_pools = {
            'fresh_biomass_kg': fresh_biomass,
            'dry_biomass_kg': dry_biomass,
            'carbon_content_kg': carbon_content_kg,
            'co2_equivalent_tonnes': co2_equivalent,
            'carbon_density_kg_per_m2': carbon_content_kg / (self.pixel_size**2),
            'total_carbon_fraction': total_carbon_fraction,
            'forest_type': forest_type
        }
        
        return carbon_pools
    
    def _safe_division(self, numerator, denominator, fill_value=0):
        """Safe division avoiding divide by zero"""
        result = np.zeros_like(numerator, dtype=float)
        valid_mask = np.abs(denominator) > 1e-8
        result[valid_mask] = numerator[valid_mask] / denominator[valid_mask]
        result[~valid_mask] = fill_value
        return result
    
    def create_summary_statistics(self, carbon_pools):
        """Create summary statistics for the carbon assessment"""
        
        # Calculate per-forest-type statistics
        forest_types = ['Non-forest', 'Coniferous', 'Deciduous', 'Mixed']
        
        summary = {
            'total_area_m2': np.prod(carbon_pools['carbon_content_kg'].shape) * self.pixel_size**2,
            'total_carbon_kg': np.sum(carbon_pools['carbon_content_kg']),
            'total_co2_tonnes': np.sum(carbon_pools['co2_equivalent_tonnes']),
            'mean_carbon_density': np.mean(carbon_pools['carbon_density_kg_per_m2']),
            'forest_type_breakdown': {}
        }
        
        for i, forest_name in enumerate(forest_types):
            mask = carbon_pools['forest_type'] == i
            if np.any(mask):
                area = np.sum(mask) * self.pixel_size**2
                total_carbon = np.sum(carbon_pools['carbon_content_kg'][mask])
                mean_density = np.mean(carbon_pools['carbon_density_kg_per_m2'][mask])
                
                summary['forest_type_breakdown'][forest_name] = {
                    'area_m2': area,
                    'area_ha': area / 10000,
                    'total_carbon_kg': total_carbon,
                    'total_carbon_tonnes': total_carbon / 1000,
                    'mean_carbon_density_kg_per_m2': mean_density,
                    'pixel_count': np.sum(mask)
                }
        
        return summary
    
    def visualize_results(self, carbon_pools, vegetation_indices, biochemical_content):
        """Create comprehensive visualization of results"""
        
        fig, axes = plt.subplots(3, 4, figsize=(20, 15))
        fig.suptitle('Spectral Carbon Pool Assessment Results', fontsize=16)
        
        # Row 1: Vegetation Indices
        im1 = axes[0, 0].imshow(vegetation_indices['lai_optimal'], cmap='Greens')
        axes[0, 0].set_title('LAI (Optimal Bands)')
        plt.colorbar(im1, ax=axes[0, 0])
        
        im2 = axes[0, 1].imshow(vegetation_indices['chlorophyll_content'], cmap='Greens')
        axes[0, 1].set_title('Chlorophyll Content')
        plt.colorbar(im2, ax=axes[0, 1])
        
        im3 = axes[0, 2].imshow(vegetation_indices['red_edge_position'], cmap='RdYlGn')
        axes[0, 2].set_title('Red Edge Position (nm)')
        plt.colorbar(im3, ax=axes[0, 2])
        
        im4 = axes[0, 3].imshow(vegetation_indices['biomass_index'], cmap='YlOrBr')
        axes[0, 3].set_title('Biomass Index')
        plt.colorbar(im4, ax=axes[0, 3])
        
        # Row 2: Biochemical Content
        im5 = axes[1, 0].imshow(biochemical_content['lignin_content'], cmap='Oranges')
        axes[1, 0].set_title('Lignin Content')
        plt.colorbar(im5, ax=axes[1, 0])
        
        im6 = axes[1, 1].imshow(biochemical_content['cellulose_content'], cmap='Blues')
        axes[1, 1].set_title('Cellulose Content')
        plt.colorbar(im6, ax=axes[1, 1])
        
        im7 = axes[1, 2].imshow(biochemical_content['water_content'], cmap='Blues')
        axes[1, 2].set_title('Water Content')
        plt.colorbar(im7, ax=axes[1, 2])
        
        # Forest type classification
        forest_colors = ['brown', 'darkgreen', 'lightgreen', 'yellow']
        forest_cmap = ListedColormap(forest_colors)
        im8 = axes[1, 3].imshow(carbon_pools['forest_type'], cmap=forest_cmap, vmin=0, vmax=3)
        axes[1, 3].set_title('Forest Type Classification')
        cbar8 = plt.colorbar(im8, ax=axes[1, 3], ticks=[0, 1, 2, 3])
        cbar8.set_ticklabels(['Non-forest', 'Coniferous', 'Deciduous', 'Mixed'])
        
        # Row 3: Carbon Results
        im9 = axes[2, 0].imshow(carbon_pools['carbon_density_kg_per_m2'], cmap='viridis')
        axes[2, 0].set_title('Carbon Density (kg/m²)')
        plt.colorbar(im9, ax=axes[2, 0])
        
        im10 = axes[2, 1].imshow(carbon_pools['co2_equivalent_tonnes'], cmap='plasma')
        axes[2, 1].set_title('CO₂ Equivalent (tonnes)')
        plt.colorbar(im10, ax=axes[2, 1])
        
        im11 = axes[2, 2].imshow(carbon_pools['total_carbon_fraction'], cmap='Spectral')
        axes[2, 2].set_title('Total Carbon Fraction')
        plt.colorbar(im11, ax=axes[2, 2])
        
        im12 = axes[2, 3].imshow(carbon_pools['dry_biomass_kg'], cmap='YlOrRd')
        axes[2, 3].set_title('Dry Biomass (kg)')
        plt.colorbar(im12, ax=axes[2, 3])
        
        plt.tight_layout()
        return fig
    
    def process_hyperspectral_image(self, file_path, wavelengths=None, output_dir='./carbon_assessment_output'):
        """Complete processing pipeline with metadata integration"""
        print("=" * 60)
        print("SPECTRAL CARBON POOL ESTIMATION WITH METADATA")
        print("=" * 60)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set processing metadata
        self.metadata_manager.set_processing_info(
            software_version="SpectralCarbonEstimator v2.0 with Metadata",
            processing_parameters={
                'pixel_size_m': self.pixel_size,
                'key_wavelengths': self.key_wavelengths,
                'carbon_factors': self.carbon_factors
            }
        )
        
        # Load hyperspectral data
        hsi_data, wavelengths = self.load_hyperspectral_image(file_path, wavelengths)
        print(f"Loaded image: {hsi_data.shape}")
        print(f"Wavelength range: {wavelengths[0]:.1f} - {wavelengths[-1]:.1f} nm")
        
        # Update metadata with spectral information
        self.metadata_manager.metadata['capture_info']['spectral_range_nm'] = f"{wavelengths[0]:.1f}-{wavelengths[-1]:.1f}"
        self.metadata_manager.metadata['capture_info']['spectral_bands'] = len(wavelengths)
        self.metadata_manager.metadata['capture_info']['spatial_resolution_m'] = self.pixel_size
        
        # Extract key bands
        band_reflectances = self.extract_key_bands(hsi_data, wavelengths)
        
        # Calculate vegetation indices
        vegetation_indices = self.calculate_vegetation_indices(band_reflectances)
        
        # Estimate biochemical content
        biochemical_content = self.estimate_biochemical_content(band_reflectances)
        
        # Estimate forest structure
        forest_structure = self.estimate_forest_structure(vegetation_indices)
        
        # Classify forest types
        forest_type = self.classify_forest_type(biochemical_content)
        
        # Calculate carbon pools
        carbon_pools = self.calculate_carbon_pools(biochemical_content, forest_structure, forest_type)
        
        # Create summary statistics
        summary = self.create_summary_statistics(carbon_pools)
        
        # Update metadata with carbon assessment results
        self.metadata_manager.update_carbon_assessment(summary)
        
        # Update metadata with detected forest types
        unique_types = np.unique(carbon_pools['forest_type'])
        type_names = ['Non-forest', 'Coniferous', 'Deciduous', 'Mixed']
        detected_types = [type_names[t] for t in unique_types if t < len(type_names)]
        self.metadata_manager.metadata['carbon_assessment']['forest_types_detected'] = detected_types
        
        # Results package
        results = {
            'carbon_pools': carbon_pools,
            'vegetation_indices': vegetation_indices,
            'biochemical_content': biochemical_content,
            'forest_structure': forest_structure,
            'summary': summary,
            'wavelengths': wavelengths,
            'key_bands': band_reflectances,
            'metadata': self.metadata_manager.metadata,
            'output_directory': output_dir
        }
        
        return results
    
    def export_complete_assessment(self, results, include_kml=True, include_geotiff=True):
        """Export complete carbon assessment with all metadata and geographic data"""
        output_dir = results['output_directory']
        base_name = self.metadata_manager.metadata['geographic_info'].get('location_name', 'carbon_assessment')
        base_name = base_name.replace(' ', '_').lower()
        
        # Get timestamp for file names
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        print(f"\nExporting complete assessment to: {output_dir}")
        print("-" * 50)
        
        exported_files = []
        
        # 1. Export metadata as JSON
        metadata_file = os.path.join(output_dir, f"{base_name}_metadata_{timestamp}.json")
        self.metadata_manager.export_metadata_json(metadata_file)
        exported_files.append(metadata_file)
        
        # 2. Export detailed carbon report
        report_file = os.path.join(output_dir, f"{base_name}_carbon_report_{timestamp}.json")
        self.metadata_manager.export_carbon_report(report_file, results['carbon_pools'])
        exported_files.append(report_file)
        
        # 3. Export KML file
        if include_kml and self.metadata_manager.metadata['geographic_info']['polygon_coordinates']:
            kml_file = os.path.join(output_dir, f"{base_name}_study_area_{timestamp}.kml")
            self.metadata_manager.generate_kml(kml_file)
            exported_files.append(kml_file)
        
        # 4. Export carbon results as CSV
        csv_file = os.path.join(output_dir, f"{base_name}_carbon_summary_{timestamp}.csv")
        self._export_carbon_csv(results, csv_file)
        exported_files.append(csv_file)
        
        # 5. Export GeoTIFF files for carbon maps
        if include_geotiff and HAS_RASTERIO:
            geotiff_files = self._export_geotiff_maps(results, output_dir, base_name, timestamp)
            exported_files.extend(geotiff_files)
        
        # 6. Save visualization plots
        plot_file = os.path.join(output_dir, f"{base_name}_visualization_{timestamp}.png")
        fig = self.visualize_results(
            results['carbon_pools'], 
            results['vegetation_indices'],
            results['biochemical_content']
        )
        fig.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close(fig)
        exported_files.append(plot_file)
        
        # 7. Create assessment summary text file
        summary_file = os.path.join(output_dir, f"{base_name}_executive_summary_{timestamp}.txt")
        self._create_text_summary(results, summary_file)
        exported_files.append(summary_file)
        
        print(f"\nExport completed! Files generated:")
        for file_path in exported_files:
            print(f"  - {os.path.basename(file_path)}")
        
        return exported_files
    
    def _export_carbon_csv(self, results, output_path):
        """Export carbon assessment results as CSV"""
        summary = results['summary']
        
        # Create summary table
        data = []
        for forest_name, forest_data in summary['forest_type_breakdown'].items():
            if forest_data['area_ha'] > 0:
                data.append({
                    'Forest_Type': forest_name,
                    'Area_Hectares': forest_data['area_ha'],
                    'Total_Carbon_Tonnes': forest_data['total_carbon_tonnes'],
                    'Carbon_Density_kg_per_m2': forest_data['mean_carbon_density_kg_per_m2'],
                    'Pixel_Count': forest_data['pixel_count']
                })
        
        # Add metadata
        metadata_row = {
            'Forest_Type': 'METADATA',
            'Area_Hectares': summary['total_area_m2'] / 10000,
            'Total_Carbon_Tonnes': summary['total_carbon_kg'] / 1000,
            'Carbon_Density_kg_per_m2': summary['mean_carbon_density'],
            'Pixel_Count': 'TOTAL'
        }
        data.append(metadata_row)
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        print(f"Carbon summary CSV exported: {os.path.basename(output_path)}")
    
    def _export_geotiff_maps(self, results, output_dir, base_name, timestamp):
        """Export carbon and other maps as GeoTIFF files"""
        if not HAS_RASTERIO:
            print("Warning: rasterio not available, skipping GeoTIFF export")
            return []
        
        exported_files = []
        
        # Get geographic bounds from metadata
        polygon_coords = self.metadata_manager.metadata['geographic_info']['polygon_coordinates']
        if not polygon_coords:
            print("Warning: No polygon coordinates available, using default bounds")
            return []
        
        # Calculate bounds
        lons = [coord[0] for coord in polygon_coords]
        lats = [coord[1] for coord in polygon_coords]
        bounds = (min(lons), min(lats), max(lons), max(lats))
        
        # Get image dimensions
        height, width = results['carbon_pools']['carbon_density_kg_per_m2'].shape
        
        # Create transform
        transform = from_bounds(*bounds, width, height)
        
        # Define maps to export
        maps_to_export = {
            'carbon_density': results['carbon_pools']['carbon_density_kg_per_m2'],
            'co2_equivalent': results['carbon_pools']['co2_equivalent_tonnes'],
            'forest_type': results['carbon_pools']['forest_type'],
            'biomass': results['carbon_pools']['dry_biomass_kg'],
            'lignin_content': results['biochemical_content']['lignin_content'],
            'cellulose_content': results['biochemical_content']['cellulose_content']
        }
        
        for map_name, map_data in maps_to_export.items():
            output_path = os.path.join(output_dir, f"{base_name}_{map_name}_{timestamp}.tif")
            
            with rasterio.open(
                output_path, 'w',
                driver='GTiff',
                height=height, width=width,
                count=1, dtype=map_data.dtype,
                crs='EPSG:4326',
                transform=transform,
                compress='lzw'
            ) as dst:
                dst.write(map_data, 1)
                
                # Add metadata
                dst.update_tags(
                    AREA_OR_POINT='Area',
                    CAPTURE_DATE=self.metadata_manager.metadata['capture_info'].get('date', 'Unknown'),
                    SENSOR_INFO=self.metadata_manager.metadata['capture_info'].get('sensor_info', 'Unknown'),
                    PROCESSING_SOFTWARE='SpectralCarbonEstimator v2.0',
                    LAND_OWNER=self.metadata_manager.metadata['landowner_info'].get('owner_name', 'Unknown'),
                    LOCATION_NAME=self.metadata_manager.metadata['geographic_info'].get('location_name', 'Unknown')
                )
            
            exported_files.append(output_path)
            print(f"GeoTIFF exported: {os.path.basename(output_path)}")
        
        return exported_files
    
    def _create_text_summary(self, results, output_path):
        """Create executive summary as text file"""
        summary = results['summary']
        metadata = self.metadata_manager.metadata
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("HYPERSPECTRAL CARBON POOL ASSESSMENT\n")
            f.write("="*50 + "\n\n")
            
            # Basic information
            f.write("ASSESSMENT OVERVIEW\n")
            f.write("-"*20 + "\n")
            f.write(f"Location: {metadata['geographic_info'].get('location_name', 'Unknown')}\n")
            f.write(f"Assessment Date: {metadata['capture_info'].get('date', 'Unknown')}\n")
            f.write(f"Total Area: {summary['total_area_m2']/10000:.1f} hectares\n")
            f.write(f"Sensor: {metadata['capture_info'].get('sensor_info', 'Unknown')}\n\n")
            
            # Landowner information
            if metadata['landowner_info'].get('owner_name'):
                f.write("PROPERTY INFORMATION\n")
                f.write("-"*20 + "\n")
                f.write(f"Owner: {metadata['landowner_info']['owner_name']}\n")
                f.write(f"Owner Type: {metadata['landowner_info'].get('owner_type', 'Unknown')}\n")
                if metadata['landowner_info'].get('property_id'):
                    f.write(f"Property ID: {metadata['landowner_info']['property_id']}\n")
                f.write(f"Land Use: {metadata['landowner_info'].get('land_use_type', 'Unknown')}\n\n")
            
            # Carbon results
            f.write("CARBON ASSESSMENT RESULTS\n")
            f.write("-"*25 + "\n")
            f.write(f"Total Carbon Stored: {summary['total_carbon_kg']/1000:.1f} tonnes\n")
            f.write(f"Total CO₂ Equivalent: {summary['total_co2_tonnes']:.1f} tonnes\n")
            f.write(f"Carbon Density: {summary['total_co2_tonnes']/(summary['total_area_m2']/10000):.1f} tonnes CO₂/ha\n\n")
            
            # Forest type breakdown
            f.write("FOREST TYPE BREAKDOWN\n")
            f.write("-"*20 + "\n")
            for forest_name, data in summary['forest_type_breakdown'].items():
                if data['area_ha'] > 0:
                    f.write(f"{forest_name}:\n")
                    f.write(f"  Area: {data['area_ha']:.1f} ha\n")
                    f.write(f"  Carbon: {data['total_carbon_tonnes']:.1f} tonnes\n")
                    f.write(f"  Density: {data['mean_carbon_density_kg_per_m2']:.2f} kg/m²\n\n")
            
            # Geographic coordinates
            if metadata['geographic_info']['polygon_coordinates']:
                f.write("STUDY AREA COORDINATES (WGS84)\n")
                f.write("-"*32 + "\n")
                for i, coord in enumerate(metadata['geographic_info']['polygon_coordinates']):
                    f.write(f"Point {i+1}: {coord[1]:.6f}°N, {coord[0]:.6f}°W\n")
                f.write(f"\nCentroid: {metadata['geographic_info'].get('centroid_lat', 0):.6f}°N, ")
                f.write(f"{metadata['geographic_info'].get('centroid_lon', 0):.6f}°W\n\n")
            
            # Processing information
            f.write("TECHNICAL DETAILS\n")
            f.write("-"*16 + "\n")
            f.write(f"Processing Date: {metadata['processing_info'].get('processing_datetime_utc', 'Unknown')}\n")
            f.write(f"Software: {metadata['processing_info'].get('software_version', 'Unknown')}\n")
            f.write(f"Spectral Range: {metadata['capture_info'].get('spectral_range_nm', 'Unknown')} nm\n")
            f.write(f"Spatial Resolution: {metadata['capture_info'].get('spatial_resolution_m', 'Unknown')} m\n")
        
        print(f"Executive summary exported: {os.path.basename(output_path)}")
        
    def print_metadata_summary(self):
        """Print summary of loaded metadata"""
        metadata = self.metadata_manager.metadata
        
        print("\n" + "="*60)
        print("METADATA SUMMARY")
        print("="*60)
        
        # Capture info
        if metadata['capture_info']:
            print("CAPTURE INFORMATION:")
            print(f"  Date: {metadata['capture_info'].get('date', 'Not set')}")
            print(f"  Sensor: {metadata['capture_info'].get('sensor_info', 'Not set')}")
            print(f"  Altitude: {metadata['capture_info'].get('flight_altitude_m', 'Not set')} m")
        
        # Geographic info
        if metadata['geographic_info']:
            print("\nGEOGRAPHIC INFORMATION:")
            print(f"  Location: {metadata['geographic_info'].get('location_name', 'Not set')}")
            print(f"  Country: {metadata['geographic_info'].get('country', 'Not set')}")
            print(f"  Area: {metadata['geographic_info'].get('area_hectares', 'Not calculated')} hectares")
            if metadata['geographic_info'].get('polygon_coordinates'):
                print(f"  Boundary: {len(metadata['geographic_info']['polygon_coordinates'])} coordinate points")
        
        # Landowner info
        if metadata['landowner_info'] and metadata['landowner_info'].get('owner_name'):
            print("\nPROPERTY INFORMATION:")
            print(f"  Owner: {metadata['landowner_info']['owner_name']}")
            print(f"  Type: {metadata['landowner_info'].get('owner_type', 'Not set')}")
            print(f"  Property ID: {metadata['landowner_info'].get('property_id', 'Not set')}")
            print(f"  Land Use: {metadata['landowner_info'].get('land_use_type', 'Not set')}")
        
        print("\n" + "="*60)
    
    def print_summary(self, results):
        """Print detailed summary of carbon assessment"""
        summary = results['summary']
        
        print("\n" + "=" * 60)
        print("CARBON POOL ASSESSMENT SUMMARY")
        print("=" * 60)
        
        print(f"Total Area: {summary['total_area_m2']:.0f} m² ({summary['total_area_m2']/10000:.1f} ha)")
        print(f"Total Carbon: {summary['total_carbon_kg']/1000:.1f} tonnes")
        print(f"Total CO₂ Equivalent: {summary['total_co2_tonnes']:.1f} tonnes")
        print(f"Mean Carbon Density: {summary['mean_carbon_density']:.2f} kg/m²")
        
        print(f"\nCarbon Density: {summary['total_co2_tonnes']/(summary['total_area_m2']/10000):.1f} tonnes CO₂/ha")
        
        print("\nFOREST TYPE BREAKDOWN:")
        print("-" * 50)
        for forest_name, data in summary['forest_type_breakdown'].items():
            if data['area_ha'] > 0:
                print(f"{forest_name:<12}: {data['area_ha']:>6.1f} ha, "
                      f"{data['total_carbon_tonnes']:>6.1f} t carbon, "
                      f"{data['mean_carbon_density_kg_per_m2']:>5.2f} kg/m²")
        
        print("\n" + "=" * 60)


def main():
    """Main execution function with comprehensive metadata example"""
    
    # Initialize the estimator
    estimator = SpectralCarbonEstimator(pixel_size=1.0)
    
    # Setup comprehensive metadata
    print("Setting up metadata...")
    estimator.setup_metadata(
        capture_datetime='2024-06-15T10:30:00Z',
        sensor_info='AVIRIS-NG Hyperspectral Imager',
        polygon_coords=[
            [-122.5, 45.5], [-122.4, 45.5], 
            [-122.4, 45.6], [-122.5, 45.6], 
            [-122.5, 45.5]  # Closed polygon
        ],
        location_name='Pacific Northwest Forest Reserve',
        owner_name='Oregon State Forest Service',
        owner_type='Government',
        property_id='OR-FOREST-001',
        contact_info='forestry@oregon.gov',
        land_use_type='Conservation',
        country='United States',
        state_province='Oregon',
        flight_altitude=1000,
        weather_conditions='Clear skies, 15°C, light winds',
        management_notes='Sustainable forestry practices, last thinning 2020'
    )
    
    # Print metadata summary
    estimator.print_metadata_summary()
    
    # Process hyperspectral image (using synthetic data for demo)
    results = estimator.process_hyperspectral_image(
        'synthetic_forest.hdr',
        output_dir='./pacific_northwest_assessment'
    )
    
    # Print carbon assessment summary
    estimator.print_summary(results)
    
    # Export complete assessment with all metadata
    exported_files = estimator.export_complete_assessment(results)
    
    # Create visualizations
    fig = estimator.visualize_results(
        results['carbon_pools'], 
        results['vegetation_indices'],
        results['biochemical_content']
    )
    plt.show()
    
    return results, exported_files

def process_real_data_with_metadata(file_path, metadata_config, output_dir=None):
    """
    Process real hyperspectral data with custom metadata configuration
    
    Parameters:
    -----------
    file_path : str
        Path to hyperspectral image file
    metadata_config : dict
        Dictionary containing all metadata information
    output_dir : str
        Output directory for results
    
    Example metadata_config:
    {
        'capture_datetime': '2024-06-15T10:30:00Z',
        'sensor_info': 'AVIRIS-NG',
        'polygon_coords': [[-122.5, 45.5], [-122.4, 45.5], ...],
        'location_name': 'My Forest',
        'owner_name': 'Forest Owner Name',
        'owner_type': 'Private',
        'property_id': 'PROP-001',
        'country': 'United States',
        'land_use_type': 'Forestry'
    }
    """
    
    estimator = SpectralCarbonEstimator(pixel_size=1.0)
    
    # Setup metadata from config
    estimator.setup_metadata(**metadata_config)
    
    # Set output directory
    if output_dir is None:
        location_name = metadata_config.get('location_name', 'forest_assessment')
        output_dir = f"./{location_name.replace(' ', '_').lower()}_results"
    
    # Process the image
    results = estimator.process_hyperspectral_image(file_path, output_dir=output_dir)
    
    # Print results
    estimator.print_summary(results)
    estimator.print_metadata_summary()
    
    # Export everything
    exported_files = estimator.export_complete_assessment(results)
    
    # Show visualizations
    estimator.visualize_results(
        results['carbon_pools'],
        results['vegetation_indices'], 
        results['biochemical_content']
    )
    plt.show()
    
    return results, exported_files

def create_kml_only(polygon_coords, metadata_dict, output_path):
    """
    Create standalone KML file with carbon assessment metadata
    
    Parameters:
    -----------
    polygon_coords : list
        List of [longitude, latitude] coordinate pairs
    metadata_dict : dict
        Dictionary with capture, landowner, and assessment metadata
    output_path : str
        Path for output KML file
    """
    
    metadata_manager = MetadataManager()
    
    # Set all metadata
    metadata_manager.set_capture_info(**metadata_dict.get('capture_info', {}))
    metadata_manager.set_geographic_info(
        polygon_coords=polygon_coords,
        **metadata_dict.get('geographic_info', {})
    )
    metadata_manager.set_landowner_info(**metadata_dict.get('landowner_info', {}))
    
    # Add carbon assessment results if available
    if 'carbon_assessment' in metadata_dict:
        metadata_manager.metadata['carbon_assessment'] = metadata_dict['carbon_assessment']
    
    # Generate KML
    kml_path = metadata_manager.generate_kml(output_path)
    return kml_path

# Example usage scenarios
def example_private_forest():
    """Example: Private forest assessment"""
    estimator = SpectralCarbonEstimator(pixel_size=2.0)
    
    estimator.setup_metadata(
        capture_datetime='2024-07-20T14:15:00Z',
        sensor_info='HySpex VNIR-1800',
        polygon_coords=[
            [-85.123, 42.456], [-85.098, 42.456],
            [-85.098, 42.478], [-85.123, 42.478],
            [-85.123, 42.456]
        ],
        location_name='Johnson Family Forest',
        owner_name='Johnson Family Trust',
        owner_type='Private',
        property_id='JOHNSON-FOREST-001',
        contact_info='info@johnsonforest.com',
        land_use_type='Sustainable Forestry',
        country='United States',
        state_province='Michigan',
        flight_altitude=800,
        weather_conditions='Partly cloudy, 22°C',
        management_notes='Certified sustainable forestry, FSC certified'
    )
    
    return estimator.process_hyperspectral_image(
        'johnson_forest.hdr',
        output_dir='./johnson_forest_assessment'
    )

def example_conservation_area():
    """Example: Conservation area assessment"""
    estimator = SpectralCarbonEstimator(pixel_size=1.5)
    
    estimator.setup_metadata(
        capture_datetime='2024-08-10T11:45:00Z',
        sensor_info='AVIRIS Classic',
        polygon_coords=[
            [-120.567, 38.789], [-120.534, 38.789],
            [-120.534, 38.812], [-120.567, 38.812],
            [-120.567, 38.789]
        ],
        location_name='Sierra Nevada Conservation Reserve',
        owner_name='Nature Conservancy',
        owner_type='NGO',
        property_id='TNC-SIERRA-005',
        contact_info='conservation@tnc.org',
        land_use_type='Conservation',
        country='United States',
        state_province='California',
        flight_altitude=1200,
        weather_conditions='Clear, 18°C, no wind',
        management_notes='Old growth forest protection, fire management zone'
    )
    
    return estimator.process_hyperspectral_image(
        'sierra_conservation.hdr',
        output_dir='./sierra_conservation_assessment'
    )

if __name__ == "__main__":
    # Run main example with comprehensive metadata
    results, files = main()
    
    print(f"\nExample completed! Check output files:")
    for file_path in files:
        print(f"  - {file_path}")
    
    # Uncomment to run other examples:
    # example_private_forest()
    # example_conservation_area()
    
    # Example of processing real data:
    # metadata_config = {
    #     'capture_datetime': '2024-06-15T10:30:00Z',
    #     'sensor_info': 'Your Sensor Name',
    #     'polygon_coords': [your_coordinates],
    #     'location_name': 'Your Forest Name',
    #     'owner_name': 'Owner Name',
    #     'owner_type': 'Private',
    #     'country': 'Your Country'
    # }
    # process_real_data_with_metadata('path/to/your/image.hdr', metadata_config)
