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
import warnings
warnings.filterwarnings('ignore')

try:
    import spectral
    HAS_SPECTRAL = True
except ImportError:
    HAS_SPECTRAL = False

try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

class SpectralCarbonEstimator:
    """
    Advanced carbon pool estimator using research-optimized spectral bands
    """
    
    def __init__(self, pixel_size=1.0):
        self.pixel_size = pixel_size
        self.key_wavelengths = self._define_key_wavelengths()
        self.vegetation_indices = {}
        self.biochemical_maps = {}
        self.carbon_factors = self._define_carbon_factors()
        
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
    
    def process_hyperspectral_image(self, file_path, wavelengths=None):
        """Complete processing pipeline"""
        print("=" * 60)
        print("SPECTRAL CARBON POOL ESTIMATION")
        print("=" * 60)
        
        # Load hyperspectral data
        hsi_data, wavelengths = self.load_hyperspectral_image(file_path, wavelengths)
        print(f"Loaded image: {hsi_data.shape}")
        print(f"Wavelength range: {wavelengths[0]:.1f} - {wavelengths[-1]:.1f} nm")
        
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
        
        # Results package
        results = {
            'carbon_pools': carbon_pools,
            'vegetation_indices': vegetation_indices,
            'biochemical_content': biochemical_content,
            'forest_structure': forest_structure,
            'summary': summary,
            'wavelengths': wavelengths,
            'key_bands': band_reflectances
        }
        
        return results
    
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
    """Main execution function"""
    
    # Initialize the estimator
    estimator = SpectralCarbonEstimator(pixel_size=1.0)
    
    # Process hyperspectral image (using synthetic data for demo)
    results = estimator.process_hyperspectral_image('synthetic_forest.hdr')
    
    # Print summary
    estimator.print_summary(results)
    
    # Create visualizations
    fig = estimator.visualize_results(
        results['carbon_pools'], 
        results['vegetation_indices'],
        results['biochemical_content']
    )
    plt.show()
    
    return results

def process_real_hyperspectral_data(file_path, wavelengths=None):
    """Process real hyperspectral data"""
    estimator = SpectralCarbonEstimator(pixel_size=1.0)
    results = estimator.process_hyperspectral_image(file_path, wavelengths)
    estimator.print_summary(results)
    
    # Show results
    estimator.visualize_results(
        results['carbon_pools'],
        results['vegetation_indices'], 
        results['biochemical_content']
    )
    plt.show()
    
    return results

if __name__ == "__main__":
    # Run with synthetic data
    results = main()
    
    # To process real data, uncomment and modify:
    # results = process_real_hyperspectral_data('path/to/your/hyperspectral_image.hdr')
