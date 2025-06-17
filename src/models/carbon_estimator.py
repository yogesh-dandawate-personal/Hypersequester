"""
Carbon Pool Estimation Model
Machine learning model for estimating carbon pools from hyperspectral data
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class CarbonEstimator:
    """
    Machine learning model for estimating carbon pools from hyperspectral data
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize the carbon estimator
        
        Args:
            model_type: Type of ML model ('random_forest', 'gradient_boosting')
        """
        self.model_type = model_type
        self.models = {}  # Separate models for different carbon pools
        self.scalers = {}
        self.is_trained = False
        
        # Carbon pools to estimate
        self.carbon_pools = [
            'above_ground_biomass',
            'below_ground_biomass',
            'dead_wood',
            'litter',
            'total_carbon'
        ]
        
        # Initialize models for each carbon pool
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models for each carbon pool"""
        
        for pool in self.carbon_pools:
            if self.model_type == 'random_forest':
                self.models[pool] = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=20,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
            elif self.model_type == 'gradient_boosting':
                self.models[pool] = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            self.scalers[pool] = StandardScaler()
    
    def prepare_features(self, reflectance_data: np.ndarray, 
                        wavelengths: np.ndarray,
                        additional_features: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
        """
        Prepare features for carbon estimation
        
        Args:
            reflectance_data: Hyperspectral reflectance data
            wavelengths: Wavelength values
            additional_features: Additional features like height, species, etc.
            
        Returns:
            Feature matrix for carbon estimation
        """
        
        features = []
        
        # Spectral features
        features.append(reflectance_data)
        
        # Vegetation indices related to biomass
        if len(wavelengths) > 50:
            # NDVI
            red_idx = np.argmin(np.abs(wavelengths - 670))
            nir_idx = np.argmin(np.abs(wavelengths - 800))
            
            red = reflectance_data[:, red_idx]
            nir = reflectance_data[:, nir_idx]
            ndvi = (nir - red) / (nir + red + 1e-8)
            features.append(ndvi.reshape(-1, 1))
            
            # Enhanced Vegetation Index (EVI)
            blue_idx = np.argmin(np.abs(wavelengths - 470))
            blue = reflectance_data[:, blue_idx]
            evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
            features.append(evi.reshape(-1, 1))
            
            # Leaf Area Index related indices
            # Red Edge Normalized Difference Vegetation Index
            red_edge_idx = np.argmin(np.abs(wavelengths - 720))
            red_edge = reflectance_data[:, red_edge_idx]
            rendvi = (red_edge - red) / (red_edge + red + 1e-8)
            features.append(rendvi.reshape(-1, 1))
            
            # Biochemical indices
            # Lignin absorption (around 1680nm)
            lignin_idx = np.argmin(np.abs(wavelengths - 1680))
            if lignin_idx < reflectance_data.shape[1]:
                lignin = reflectance_data[:, lignin_idx]
                features.append(lignin.reshape(-1, 1))
            
            # Cellulose absorption (around 2100nm)
            cellulose_idx = np.argmin(np.abs(wavelengths - 2100))
            if cellulose_idx < reflectance_data.shape[1]:
                cellulose = reflectance_data[:, cellulose_idx]
                features.append(cellulose.reshape(-1, 1))
            
            # Water content indices
            water_1450_idx = np.argmin(np.abs(wavelengths - 1450))
            water_1940_idx = np.argmin(np.abs(wavelengths - 1940))
            
            if water_1450_idx < reflectance_data.shape[1]:
                water_1450 = reflectance_data[:, water_1450_idx]
                features.append(water_1450.reshape(-1, 1))
            
            if water_1940_idx < reflectance_data.shape[1]:
                water_1940 = reflectance_data[:, water_1940_idx]
                features.append(water_1940.reshape(-1, 1))
        
        # Additional features if provided
        if additional_features:
            for feature_name, feature_data in additional_features.items():
                if feature_data.ndim == 1:
                    feature_data = feature_data.reshape(-1, 1)
                features.append(feature_data)
        
        # Concatenate all features
        feature_matrix = np.concatenate(features, axis=1)
        
        return feature_matrix
    
    def train(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train carbon estimation models
        
        Args:
            training_data: Dictionary containing reflectance, wavelengths, and carbon measurements
            
        Returns:
            Training results and metrics
        """
        
        logger.info(f"Training {self.model_type} carbon estimation models")
        
        # Extract training data
        reflectance = training_data['reflectance']
        wavelengths = training_data['wavelengths']
        carbon_measurements = training_data['carbon_measurements']
        additional_features = training_data.get('additional_features')
        
        # Prepare features
        features = self.prepare_features(reflectance, wavelengths, additional_features)
        
        results = {}
        
        # Train separate model for each carbon pool
        for pool in self.carbon_pools:
            if pool not in carbon_measurements:
                logger.warning(f"No training data for carbon pool: {pool}")
                continue
            
            logger.info(f"Training model for {pool}")
            
            # Get target values
            y = carbon_measurements[pool]
            
            # Scale features
            X_scaled = self.scalers[pool].fit_transform(features)
            
            # Split data
            X_train, X_val, y_train, y_val = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.models[pool].fit(X_train, y_train)
            
            # Evaluate model
            train_pred = self.models[pool].predict(X_train)
            val_pred = self.models[pool].predict(X_val)
            
            # Calculate metrics
            train_r2 = r2_score(y_train, train_pred)
            val_r2 = r2_score(y_val, val_pred)
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            val_mae = mean_absolute_error(y_val, val_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(
                self.models[pool], X_scaled, y, cv=5, scoring='r2'
            )
            
            results[pool] = {
                'train_r2': train_r2,
                'validation_r2': val_r2,
                'validation_rmse': val_rmse,
                'validation_mae': val_mae,
                'cv_mean_r2': cv_scores.mean(),
                'cv_std_r2': cv_scores.std(),
                'n_samples': len(X_scaled)
            }
            
            logger.info(f"{pool} - Validation R²: {val_r2:.3f}, RMSE: {val_rmse:.2f}")
        
        self.is_trained = True
        
        return results
    
    def predict(self, reflectance_data: np.ndarray, 
                wavelengths: np.ndarray,
                additional_features: Optional[Dict[str, np.ndarray]] = None) -> Dict[str, Any]:
        """
        Predict carbon pools from hyperspectral data
        
        Args:
            reflectance_data: Hyperspectral reflectance data
            wavelengths: Wavelength values
            additional_features: Additional features
            
        Returns:
            Carbon pool predictions
        """
        
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        # Prepare features
        features = self.prepare_features(reflectance_data, wavelengths, additional_features)
        
        predictions = {}
        
        # Make predictions for each carbon pool
        for pool in self.carbon_pools:
            if pool in self.models:
                # Scale features
                X_scaled = self.scalers[pool].transform(features)
                
                # Predict
                pred = self.models[pool].predict(X_scaled)
                predictions[pool] = pred
        
        # Calculate total carbon if individual pools are predicted
        if all(pool in predictions for pool in ['above_ground_biomass', 'below_ground_biomass', 'dead_wood', 'litter']):
            predictions['calculated_total'] = (
                predictions['above_ground_biomass'] + 
                predictions['below_ground_biomass'] + 
                predictions['dead_wood'] + 
                predictions['litter']
            )
        
        return predictions
    
    def save_models(self, model_dir: str):
        """Save all trained models to disk"""
        
        if not self.is_trained:
            raise ValueError("Cannot save untrained models")
        
        import os
        os.makedirs(model_dir, exist_ok=True)
        
        for pool in self.carbon_pools:
            if pool in self.models:
                model_data = {
                    'model': self.models[pool],
                    'scaler': self.scalers[pool],
                    'model_type': self.model_type
                }
                
                model_path = os.path.join(model_dir, f'{pool}_model.joblib')
                joblib.dump(model_data, model_path)
        
        logger.info(f"Models saved to {model_dir}")
    
    def load_models(self, model_dir: str):
        """Load trained models from disk"""
        
        import os
        
        for pool in self.carbon_pools:
            model_path = os.path.join(model_dir, f'{pool}_model.joblib')
            
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.models[pool] = model_data['model']
                self.scalers[pool] = model_data['scaler']
        
        self.is_trained = True
        logger.info(f"Models loaded from {model_dir}")

def create_sample_carbon_data() -> Dict[str, Any]:
    """
    Create sample carbon training data for testing
    This would normally come from field measurements
    """
    
    np.random.seed(42)
    
    n_samples = 500
    n_bands = 200
    wavelengths = np.linspace(400, 2500, n_bands)
    
    # Simulate hyperspectral data
    reflectance = 0.1 + 0.3 * np.random.random((n_samples, n_bands))
    
    # Simulate carbon measurements (tonnes per hectare)
    carbon_measurements = {
        'above_ground_biomass': 50 + 100 * np.random.random(n_samples),
        'below_ground_biomass': 10 + 20 * np.random.random(n_samples),
        'dead_wood': 2 + 8 * np.random.random(n_samples),
        'litter': 1 + 4 * np.random.random(n_samples)
    }
    
    # Calculate total carbon
    carbon_measurements['total_carbon'] = (
        carbon_measurements['above_ground_biomass'] + 
        carbon_measurements['below_ground_biomass'] + 
        carbon_measurements['dead_wood'] + 
        carbon_measurements['litter']
    )
    
    # Additional features (tree height, species index, etc.)
    additional_features = {
        'tree_height': 10 + 30 * np.random.random(n_samples),
        'species_index': np.random.randint(0, 4, n_samples)
    }
    
    return {
        'reflectance': reflectance,
        'wavelengths': wavelengths,
        'carbon_measurements': carbon_measurements,
        'additional_features': additional_features
    }
