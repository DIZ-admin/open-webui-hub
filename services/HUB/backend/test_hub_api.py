#!/usr/bin/env python3
"""
Unit tests for Hub Service API
Tests all API endpoints and core functionality
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from app import app, _fetch_service_status, _fetch_all_services, _fetch_architecture_data

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_docker_client():
    """Mock Docker client"""
    mock_client = MagicMock()
    mock_container = MagicMock()
    mock_container.status = 'running'
    mock_container.name = 'open-webui-hub-test-1'
    mock_client.containers.get.return_value = mock_container
    return mock_client

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'hub-api'
        assert 'uptime_seconds' in data
        assert 'timestamp' in data

    def test_health_check_includes_docker_status(self, client):
        """Test health check includes Docker availability"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'docker_available' in data

class TestServicesEndpoint:
    """Test services endpoints"""
    
    @patch('app.docker_client')
    @patch('app.requests.get')
    def test_get_all_services(self, mock_requests, mock_docker, client):
        """Test getting all services"""
        # Mock Docker response
        mock_container = MagicMock()
        mock_container.status = 'running'
        mock_docker.containers.get.return_value = mock_container
        
        # Mock HTTP health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        response = client.get('/api/services')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'services' in data
        assert 'total' in data
        assert isinstance(data['services'], list)

    def test_get_specific_service_not_found(self, client):
        """Test getting non-existent service"""
        response = client.get('/api/services/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data

    @patch('app.docker_client')
    def test_get_specific_service_success(self, mock_docker, client):
        """Test getting specific service"""
        # Mock Docker response
        mock_container = MagicMock()
        mock_container.status = 'running'
        mock_docker.containers.get.return_value = mock_container
        
        response = client.get('/api/services/nginx')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['id'] == 'nginx'
        assert data['name'] == 'Nginx'

class TestArchitectureEndpoint:
    """Test architecture endpoint"""
    
    @patch('app.docker_client')
    @patch('app.requests.get')
    def test_get_architecture(self, mock_requests, mock_docker, client):
        """Test getting architecture data"""
        # Mock Docker response
        mock_container = MagicMock()
        mock_container.status = 'running'
        mock_docker.containers.get.return_value = mock_container
        
        # Mock HTTP health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        response = client.get('/api/architecture')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'services' in data
        assert 'layers' in data
        assert 'total_services' in data
        assert 'healthy_services' in data
        assert 'running_containers' in data

class TestLayersEndpoint:
    """Test layers endpoint"""
    
    def test_get_layers(self, client):
        """Test getting architecture layers"""
        response = client.get('/api/layers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'layers' in data
        assert isinstance(data['layers'], list)
        
        # Check that all expected layers are present
        layer_ids = [layer['id'] for layer in data['layers']]
        expected_layers = ['presentation', 'application', 'service', 'data', 'infrastructure']
        for expected_layer in expected_layers:
            assert expected_layer in layer_ids

class TestServiceDiscoveryEndpoint:
    """Test service discovery endpoint"""
    
    @patch('app.docker_client')
    def test_service_discovery_enabled(self, mock_docker, client):
        """Test service discovery when enabled"""
        # Mock Docker containers
        mock_container = MagicMock()
        mock_container.name = 'open-webui-hub-nginx-1'
        mock_container.status = 'running'
        mock_container.image.tags = ['nginx:latest']
        mock_container.ports = {'80/tcp': [{'HostPort': '80'}]}
        mock_container.labels = {}
        mock_docker.containers.list.return_value = [mock_container]
        
        response = client.get('/api/discovery')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'discovered_services' in data
        assert 'configured_services' in data

    @patch('app.CONFIG', {'enable_service_discovery': False})
    def test_service_discovery_disabled(self, client):
        """Test service discovery when disabled"""
        response = client.get('/api/discovery')
        assert response.status_code == 403
        
        data = json.loads(response.data)
        assert 'error' in data

class TestMetricsEndpoint:
    """Test metrics endpoint"""
    
    @patch('app.docker_client')
    @patch('app.requests.get')
    def test_get_metrics(self, mock_requests, mock_docker, client):
        """Test getting system metrics"""
        # Mock Docker response
        mock_container = MagicMock()
        mock_container.status = 'running'
        mock_docker.containers.get.return_value = mock_container
        
        # Mock HTTP health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        response = client.get('/api/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_services' in data
        assert 'healthy_services' in data
        assert 'running_containers' in data
        assert 'error_services' in data
        assert 'layers' in data
        assert 'uptime' in data
        assert 'layer_metrics' in data

class TestCacheEndpoints:
    """Test cache management endpoints"""
    
    def test_cache_info(self, client):
        """Test getting cache information"""
        response = client.get('/api/cache/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'cache_size' in data
        assert 'cache_keys' in data
        assert 'cache_ttl' in data

    def test_clear_cache(self, client):
        """Test clearing cache"""
        response = client.post('/api/cache/clear')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data

class TestServiceStatusFunctions:
    """Test internal service status functions"""
    
    @patch('app.docker_client')
    @patch('app.requests.get')
    def test_fetch_service_status_healthy(self, mock_requests, mock_docker):
        """Test fetching status for healthy service"""
        # Mock Docker response
        mock_container = MagicMock()
        mock_container.status = 'running'
        mock_docker.containers.get.return_value = mock_container
        
        # Mock HTTP health check
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        config = {
            'name': 'Test Service',
            'category': 'Test',
            'layer': 'test',
            'port': 8080,
            'container_name': 'test-container',
            'health_url': 'http://test:8080/health',
            'description': 'Test service'
        }
        
        result = _fetch_service_status('test', config)
        
        assert result['id'] == 'test'
        assert result['container_status'] == 'running'
        assert result['health_status'] == 'healthy'
        assert result['status'] == 'Production Ready'

    @patch('app.docker_client')
    def test_fetch_service_status_no_health_url(self, mock_docker):
        """Test fetching status for service without health URL"""
        # Mock Docker response
        mock_container = MagicMock()
        mock_container.status = 'running'
        mock_docker.containers.get.return_value = mock_container
        
        config = {
            'name': 'Test Service',
            'category': 'Test',
            'layer': 'test',
            'port': 8080,
            'container_name': 'test-container',
            'health_url': None,
            'description': 'Test service'
        }
        
        result = _fetch_service_status('test', config)
        
        assert result['id'] == 'test'
        assert result['container_status'] == 'running'
        assert result['health_status'] == 'unknown'

class TestErrorHandling:
    """Test error handling"""
    
    @patch('app._fetch_all_services')
    def test_services_endpoint_error(self, mock_fetch, client):
        """Test services endpoint error handling"""
        mock_fetch.side_effect = Exception("Test error")
        
        response = client.get('/api/services')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
