#!/usr/bin/env python3
"""
Integration tests for Hub Service
Tests real Docker integration and API functionality
"""

import pytest
import requests
import time
import json
import subprocess
import os
from typing import Dict, Any

# Test configuration
HUB_API_URL = os.getenv('HUB_API_URL', 'http://localhost:5003')
DOCKER_COMPOSE_FILE = os.getenv('DOCKER_COMPOSE_FILE', 'compose.local.yml')
TEST_TIMEOUT = 30

class TestHubServiceIntegration:
    """Integration tests for Hub Service"""
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        """Setup for integration tests"""
        print(f"Testing Hub API at: {HUB_API_URL}")
        
        # Wait for service to be ready
        self.wait_for_service_ready()
        
        yield
        
        # Cleanup if needed
        pass
    
    def wait_for_service_ready(self, timeout: int = TEST_TIMEOUT):
        """Wait for Hub service to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{HUB_API_URL}/api/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Hub service is ready")
                    return
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        pytest.fail(f"Hub service not ready after {timeout} seconds")
    
    def test_health_endpoint(self):
        """Test health endpoint returns correct data"""
        response = requests.get(f"{HUB_API_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'hub-api'
        assert 'uptime_seconds' in data
        assert 'docker_available' in data
        assert isinstance(data['uptime_seconds'], (int, float))
        
        print(f"✅ Health check passed - Uptime: {data['uptime_seconds']:.1f}s")
    
    def test_services_endpoint(self):
        """Test services endpoint returns valid data"""
        response = requests.get(f"{HUB_API_URL}/api/services")
        assert response.status_code == 200
        
        data = response.json()
        assert 'services' in data
        assert 'total' in data
        assert isinstance(data['services'], list)
        assert len(data['services']) > 0
        
        # Validate service structure
        for service in data['services']:
            assert 'id' in service
            assert 'name' in service
            assert 'category' in service
            assert 'layer' in service
            assert 'container_status' in service
            assert 'health_status' in service
            assert 'description' in service
        
        print(f"✅ Services endpoint passed - Found {len(data['services'])} services")
    
    def test_architecture_endpoint(self):
        """Test architecture endpoint returns complete data"""
        response = requests.get(f"{HUB_API_URL}/api/architecture")
        assert response.status_code == 200
        
        data = response.json()
        assert 'services' in data
        assert 'layers' in data
        assert 'total_services' in data
        assert 'healthy_services' in data
        assert 'running_containers' in data
        
        # Validate layers structure
        assert isinstance(data['layers'], list)
        assert len(data['layers']) >= 5  # Expected architecture layers
        
        for layer in data['layers']:
            assert 'id' in layer
            assert 'name' in layer
            assert 'description' in layer
            assert 'color' in layer
            assert 'services' in layer
        
        print(f"✅ Architecture endpoint passed - {data['total_services']} services, {len(data['layers'])} layers")
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint returns performance data"""
        response = requests.get(f"{HUB_API_URL}/api/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert 'total_services' in data
        assert 'healthy_services' in data
        assert 'running_containers' in data
        assert 'error_services' in data
        assert 'layers' in data
        assert 'uptime' in data
        assert 'layer_metrics' in data
        
        # Validate metrics values
        assert isinstance(data['total_services'], int)
        assert isinstance(data['healthy_services'], int)
        assert isinstance(data['running_containers'], int)
        assert data['total_services'] >= 0
        assert data['healthy_services'] >= 0
        assert data['running_containers'] >= 0
        
        print(f"✅ Metrics endpoint passed - {data['healthy_services']}/{data['total_services']} healthy services")
    
    def test_layers_endpoint(self):
        """Test layers endpoint returns architecture layers"""
        response = requests.get(f"{HUB_API_URL}/api/layers")
        assert response.status_code == 200
        
        data = response.json()
        assert 'layers' in data
        assert isinstance(data['layers'], list)
        
        # Check for expected layers
        layer_ids = [layer['id'] for layer in data['layers']]
        expected_layers = ['presentation', 'application', 'service', 'data', 'infrastructure']
        
        for expected_layer in expected_layers:
            assert expected_layer in layer_ids, f"Missing layer: {expected_layer}"
        
        print(f"✅ Layers endpoint passed - Found all {len(expected_layers)} expected layers")
    
    def test_service_discovery_endpoint(self):
        """Test service discovery endpoint"""
        response = requests.get(f"{HUB_API_URL}/api/discovery")
        
        # Service discovery might be disabled, so check for both cases
        if response.status_code == 403:
            data = response.json()
            assert 'error' in data
            print("ℹ️ Service discovery is disabled")
        else:
            assert response.status_code == 200
            data = response.json()
            assert 'discovered_services' in data
            assert 'configured_services' in data
            print(f"✅ Service discovery passed - Found {len(data['discovered_services'])} discovered services")
    
    def test_cache_endpoints(self):
        """Test cache management endpoints"""
        # Test cache info
        response = requests.get(f"{HUB_API_URL}/api/cache/info")
        assert response.status_code == 200
        
        data = response.json()
        assert 'cache_size' in data
        assert 'cache_keys' in data
        assert 'cache_ttl' in data
        
        # Test cache clear
        response = requests.post(f"{HUB_API_URL}/api/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert 'message' in data
        
        print("✅ Cache endpoints passed")
    
    def test_specific_service_endpoint(self):
        """Test getting specific service data"""
        # Test valid service
        response = requests.get(f"{HUB_API_URL}/api/services/nginx")
        assert response.status_code == 200
        
        data = response.json()
        assert data['id'] == 'nginx'
        assert data['name'] == 'Nginx'
        
        # Test invalid service
        response = requests.get(f"{HUB_API_URL}/api/services/nonexistent")
        assert response.status_code == 404
        
        print("✅ Specific service endpoint passed")
    
    def test_frontend_serving(self):
        """Test that frontend files are served correctly"""
        # Test main page
        response = requests.get(f"{HUB_API_URL}/")
        assert response.status_code == 200
        assert 'text/html' in response.headers.get('content-type', '')
        
        # Test API vs frontend routing
        api_response = requests.get(f"{HUB_API_URL}/api/health")
        frontend_response = requests.get(f"{HUB_API_URL}/some-frontend-route")
        
        assert api_response.status_code == 200
        assert frontend_response.status_code == 200
        
        print("✅ Frontend serving passed")
    
    def test_response_times(self):
        """Test API response times are acceptable"""
        endpoints = [
            '/api/health',
            '/api/services',
            '/api/architecture',
            '/api/metrics',
            '/api/layers'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{HUB_API_URL}{endpoint}")
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0, f"Endpoint {endpoint} took {response_time:.2f}s (too slow)"
            
            print(f"✅ {endpoint}: {response_time:.3f}s")
    
    def test_data_consistency(self):
        """Test data consistency across endpoints"""
        # Get data from different endpoints
        services_response = requests.get(f"{HUB_API_URL}/api/services")
        architecture_response = requests.get(f"{HUB_API_URL}/api/architecture")
        metrics_response = requests.get(f"{HUB_API_URL}/api/metrics")
        
        services_data = services_response.json()
        architecture_data = architecture_response.json()
        metrics_data = metrics_response.json()
        
        # Check consistency
        assert len(services_data['services']) == architecture_data['total_services']
        assert architecture_data['total_services'] == metrics_data['total_services']
        assert architecture_data['healthy_services'] == metrics_data['healthy_services']
        assert architecture_data['running_containers'] == metrics_data['running_containers']
        
        print("✅ Data consistency check passed")

class TestDockerIntegration:
    """Test Docker integration functionality"""
    
    def test_docker_container_detection(self):
        """Test that Hub service can detect Docker containers"""
        response = requests.get(f"{HUB_API_URL}/api/services")
        assert response.status_code == 200
        
        data = response.json()
        services = data['services']
        
        # Check that at least some services have container status
        container_statuses = [s.get('container_status') for s in services]
        assert 'running' in container_statuses or 'exited' in container_statuses
        
        print("✅ Docker container detection passed")
    
    def test_health_check_integration(self):
        """Test health check integration with actual services"""
        response = requests.get(f"{HUB_API_URL}/api/services")
        data = response.json()
        
        # Count services with health checks
        health_statuses = [s.get('health_status') for s in data['services']]
        healthy_count = health_statuses.count('healthy')
        
        print(f"✅ Health check integration - {healthy_count} healthy services detected")

def run_integration_tests():
    """Run integration tests with proper setup"""
    print("🚀 Starting Hub Service Integration Tests")
    print(f"Target URL: {HUB_API_URL}")
    print(f"Docker Compose: {DOCKER_COMPOSE_FILE}")
    print("-" * 50)
    
    # Run pytest
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        f'--timeout={TEST_TIMEOUT}'
    ])
    
    return exit_code

if __name__ == '__main__':
    exit_code = run_integration_tests()
    exit(exit_code)
