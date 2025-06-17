"""
Species Classification Model
Machine learning model for identifying forest species from hyperspectral data
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class SpeciesClassifier:
    """
    Machine learning model for forest species classification
    using hyperspectral reflectance data
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize the species classifier
        
        Args:
            model_type: Type of ML model ('random_forest', 'svm', 'ensemble')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.species_labels = {}
        self.feature_importance = None
        self.is_trained = False
        
        # Initialize model based on type
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the machine learning model"""
        
        if self.model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'svm':
            self.model = SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def prepare_features(self, reflectance_data: np.ndarray, 
                        wavelengths: np.ndarray) -> np.ndarray:
        """
        Prepare features from hyperspectral reflectance data
        
        Args:
            reflectance_data: Reflectance values (n_samples, n_bands)
            wavelengths: Wavelength values for each band
            
        Returns:
            Feature matrix for classification
        """
        
        features = []
        
        # Raw reflectance values
        features.append(reflectance_data)
        
        # Vegetation indices
        if len(wavelengths) > 50:  # Ensure we have enough bands
            # NDVI (if NIR and Red bands are available)
            red_idx = np.argmin(np.abs(wavelengths - 670))
            nir_idx = np.argmin(np.abs(wavelengths - 800))
            
            red = reflectance_data[:, red_idx]
            nir = reflectance_data[:, nir_idx]
            ndvi = (nir - red) / (nir + red + 1e-8)
            features.append(ndvi.reshape(-1, 1))
            
            # Red Edge Position
            red_edge_start = np.argmin(np.abs(wavelengths - 680))
            red_edge_end = np.argmin(np.abs(wavelengths - 750))
            red_edge_bands = reflectance_data[:, red_edge_start:red_edge_end]
            red_edge_pos = np.argmax(np.gradient(red_edge_bands, axis=1), axis=1)
            features.append(red_edge_pos.reshape(-1, 1))
            
            # Water absorption features
            water_1450_idx = np.argmin(np.abs(wavelengths - 1450))
            water_1940_idx = np.argmin(np.abs(wavelengths - 1940))
            
            if water_1450_idx < reflectance_data.shape[1]:
                water_1450 = reflectance_data[:, water_1450_idx]
                features.append(water_1450.reshape(-1, 1))
            
            if water_1940_idx < reflectance_data.shape[1]:
                water_1940 = reflectance_data[:, water_1940_idx]
                features.append(water_1940.reshape(-1, 1))
        
        # Concatenate all features
        feature_matrix = np.concatenate(features, axis=1)
        
        return feature_matrix
    
    def train(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train the species classification model
        
        Args:
            training_data: Dictionary containing reflectance data, wavelengths, and labels
            
        Returns:
            Training results and metrics
        """
        
        logger.info(f"Training {self.model_type} species classifier")
        
        # Extract training data
        reflectance = training_data['reflectance']
        wavelengths = training_data['wavelengths']
        species_labels = training_data['species_labels']
        
        # Prepare features
        features = self.prepare_features(reflectance, wavelengths)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Create label mapping
        unique_species = np.unique(species_labels)
        self.species_labels = {i: species for i, species in enumerate(unique_species)}
        label_to_idx = {species: i for i, species in self.species_labels.items()}
        
        # Convert labels to indices
        y = np.array([label_to_idx[label] for label in species_labels])
        
        # Split data for validation
        X_train, X_val, y_train, y_val = train_test_split(
            features_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate model
        train_score = self.model.score(X_train, y_train)
        val_score = self.model.score(X_val, y_val)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, features_scaled, y, cv=5)
        
        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = self.model.feature_importances_
        
        # Predictions for detailed metrics
        y_pred = self.model.predict(X_val)
        
        results = {
            'train_accuracy': train_score,
            'validation_accuracy': val_score,
            'cv_mean_accuracy': cv_scores.mean(),
            'cv_std_accuracy': cv_scores.std(),
            'classification_report': classification_report(
                y_val, y_pred, target_names=list(unique_species), output_dict=True
            ),
            'n_samples': len(features_scaled),
            'n_features': features_scaled.shape[1],
            'n_species': len(unique_species)
        }
        
        logger.info(f"Training completed. Validation accuracy: {val_score:.3f}")
        
        return results
    
    def predict(self, reflectance_data: np.ndarray, 
                wavelengths: np.ndarray) -> Dict[str, Any]:
        """
        Predict species from hyperspectral data
        
        Args:
            reflectance_data: Reflectance values
            wavelengths: Wavelength values
            
        Returns:
            Prediction results with probabilities
        """
        
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Prepare features
        features = self.prepare_features(reflectance_data, wavelengths)
        features_scaled = self.scaler.transform(features)
        
        # Make predictions
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        # Convert predictions to species names
        predicted_species = [self.species_labels[pred] for pred in predictions]
        
        # Get confidence scores
        confidence_scores = np.max(probabilities, axis=1)
        
        results = {
            'predicted_species': predicted_species,
            'confidence_scores': confidence_scores,
            'probabilities': probabilities,
            'species_labels': list(self.species_labels.values())
        }
        
        return results
    
    def save_model(self, model_path: str):
        """Save the trained model to disk"""
        
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'species_labels': self.species_labels,
            'model_type': self.model_type,
            'feature_importance': self.feature_importance
        }
        
        joblib.dump(model_data, model_path)
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: str):
        """Load a trained model from disk"""
        
        model_data = joblib.load(model_path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.species_labels = model_data['species_labels']
        self.model_type = model_data['model_type']
        self.feature_importance = model_data.get('feature_importance')
        self.is_trained = True
        
        logger.info(f"Model loaded from {model_path}")

def create_sample_training_data() -> Dict[str, Any]:
    """
    Create sample training data for testing
    This would normally come from field measurements and spectral libraries
    """
    
    np.random.seed(42)
    
    # Simulate hyperspectral data for different species
    n_samples_per_species = 100
    n_bands = 200
    wavelengths = np.linspace(400, 2500, n_bands)
    
    species = ['Douglas Fir', 'Western Hemlock', 'Red Cedar', 'Bigleaf Maple']
    
    all_reflectance = []
    all_labels = []
    
    for i, species_name in enumerate(species):
        # Create species-specific spectral signatures
        base_reflectance = 0.1 + 0.3 * np.random.random((n_samples_per_species, n_bands))
        
        # Add species-specific characteristics
        if 'Fir' in species_name:
            # Higher NIR reflectance
            nir_indices = (wavelengths >= 700) & (wavelengths <= 1300)
            base_reflectance[:, nir_indices] += 0.2
        elif 'Hemlock' in species_name:
            # Different red edge position
            red_edge_indices = (wavelengths >= 680) & (wavelengths <= 750)
            base_reflectance[:, red_edge_indices] += 0.15
        elif 'Cedar' in species_name:
            # Higher water absorption
            water_indices = (wavelengths >= 1400) & (wavelengths <= 1500)
            base_reflectance[:, water_indices] -= 0.1
        
        all_reflectance.append(base_reflectance)
        all_labels.extend([species_name] * n_samples_per_species)
    
    reflectance_data = np.vstack(all_reflectance)
    
    return {
        'reflectance': reflectance_data,
        'wavelengths': wavelengths,
        'species_labels': all_labels
    }
