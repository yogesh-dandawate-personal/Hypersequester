"""
Tests for core processing functionality
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.core.processor import HypersequesterProcessor
from src.utils.helpers import validate_coordinates, calculate_carbon_metrics

class TestHypersequesterProcessor:
    """Test cases for the main processor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.processor = HypersequesterProcessor()
        self.sample_metadata = {
            'capture_datetime': '2024-06-15T10:30:00Z',
            'sensor_info': 'Test Sensor',
            'polygon_coords': [[-122.5, 45.5], [-122.4, 45.5], [-122.4, 45.6], [-122.5, 45.6]],
            'location_name': 'Test Forest',
            'owner_name': 'Test Owner',
            'country': 'USA'
        }
    
    def test_processor_initialization(self):
        """Test processor initialization"""
        assert self.processor is not None
        assert self.processor.pixel_size == 1.0
        assert self.processor.estimator is None
    
    def test_processor_with_config(self):
        """Test processor initialization with config"""
        config = {'pixel_size': 2.0}
        processor = HypersequesterProcessor(config)
        assert processor.pixel_size == 2.0
    
    @patch('src.core.processor.SpectralCarbonEstimator')
    def test_process_assessment_success(self, mock_estimator_class):
        """Test successful assessment processing"""
        # Mock the estimator
        mock_estimator = Mock()
        mock_estimator_class.return_value = mock_estimator
        mock_estimator.metadata_manager.metadata = {'test': 'data'}
        
        # Mock methods
        mock_estimator.setup_metadata.return_value = None
        mock_estimator.metadata_manager.update_carbon_assessment.return_value = None
        mock_estimator.metadata_manager.generate_kml.return_value = 'test.kml'
        mock_estimator.metadata_manager.export_metadata_json.return_value = 'metadata.json'
        mock_estimator.metadata_manager.export_carbon_report.return_value = 'report.json'
        
        # Test processing
        result = self.processor.process_assessment(
            'test_input.dat',
            'test_output',
            self.sample_metadata
        )
        
        assert result['status'] == 'completed'
        assert 'carbon_results' in result
        assert 'output_files' in result
        assert 'metadata' in result

class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_validate_coordinates_valid(self):
        """Test coordinate validation with valid coordinates"""
        valid_coords = [[-122.5, 45.5], [-122.4, 45.5], [-122.4, 45.6], [-122.5, 45.6]]
        assert validate_coordinates(valid_coords) is True
    
    def test_validate_coordinates_invalid(self):
        """Test coordinate validation with invalid coordinates"""
        # Too few points
        assert validate_coordinates([[-122.5, 45.5], [-122.4, 45.5]]) is False
        
        # Invalid longitude
        assert validate_coordinates([[-200, 45.5], [-122.4, 45.5], [-122.4, 45.6]]) is False
        
        # Invalid latitude
        assert validate_coordinates([[-122.5, 95], [-122.4, 45.5], [-122.4, 45.6]]) is False
    
    def test_calculate_carbon_metrics(self):
        """Test carbon metrics calculation"""
        carbon_data = {
            'total_carbon_kg': 50000,
            'area_hectares': 100
        }
        
        metrics = calculate_carbon_metrics(carbon_data)
        
        assert metrics['total_carbon_tonnes'] == 50.0
        assert metrics['co2_equivalent_tonnes'] == pytest.approx(183.5, rel=1e-2)
        assert metrics['carbon_density_tonnes_per_hectare'] == pytest.approx(1.835, rel=1e-2)
    
    def test_calculate_carbon_metrics_zero_area(self):
        """Test carbon metrics calculation with zero area"""
        carbon_data = {
            'total_carbon_kg': 50000,
            'area_hectares': 0
        }
        
        metrics = calculate_carbon_metrics(carbon_data)
        assert metrics['carbon_density_tonnes_per_hectare'] == 0

if __name__ == '__main__':
    pytest.main([__file__])
