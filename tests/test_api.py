"""
Unit tests for API endpoints in main/api.py
"""
import pytest
from sqlalchemy import text
from app import app, db


class TestHealthEndpoint:
    """Tests for /api/v1/health endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check returns healthy status when database is connected"""
        response = client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'


class TestWardsCandidatesEndpoint:
    """Tests for /api/v1/wards/<ward_id>/candidates endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self, client):
        """Set up test candidate data before each test"""
        with app.app_context():
            # Insert test candidates using actual table structure
            insert_query = text("""
                INSERT INTO candidates (full_names, ward_code, candidate_type, locator, party)
                VALUES (:full_names, :ward_code, :candidate_type, :locator, :party)
            """)
            
            # Insert at least 2 candidates for WARD001 with different types
            test_candidates = [
               
                {
                    'full_names': 'Bob Johnson',
                    'ward_code': 'WARD001',
                    'candidate_type': 'national',
                    'locator': '{ward_code}',
                    'party': 'Party B'
                },
                {
                    'full_names': 'David Wilson',
                    'ward_code': 'WARD002',
                    'candidate_type': 'provincial',
                    'locator': '{ward_code}',
                    'party': 'Party D'
                }
            ]
            
            for candidate in test_candidates:
                db.session.execute(insert_query, candidate)
            
            db.session.commit()
            
        yield
        
        # Cleanup after test - only delete test data we inserted
        with app.app_context():
            db.session.execute(text("DELETE FROM candidates WHERE ward_code IN ('WARD001', 'WARD002')"))
            db.session.commit()
    
    def test_get_candidates_by_ward_id(self, client):
        """Test retrieving candidates by ward_id"""
        response = client.get('/api/v1/wards/WARD001/candidates')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ward_id'] == 'WARD001'
        assert 'candidates' in data
        assert 'count' in data
        assert data['count'] >= 2
    
    def test_get_candidates_with_candidate_type_filter(self, client):
        """Test filtering candidates by candidate_type"""
        response = client.get('/api/v1/wards/WARD001/candidates?candidate_type=national')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ward_id'] == 'WARD001'
        assert data['count'] >= 2
        for candidate in data['candidates']:
            assert candidate['candidate_type'] == 'national'
    
    def test_get_candidates_ward_not_found(self, client):
        """Test retrieving candidates for a non-existent ward_id"""
        response = client.get('/api/v1/wards/NONEXISTENT/candidates')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['ward_id'] == 'NONEXISTENT'
        assert data['count'] == 0
        assert data['candidates'] == []

