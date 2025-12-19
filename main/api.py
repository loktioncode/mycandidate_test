"""
REST API endpoints for MyCandidate application
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from .app import app, db
from .decorators import get_candidates

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint for load balancers and monitoring
    """
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503


@api_bp.route('/wards/<ward_id>/candidates', methods=['GET'])
def get_ward_candidates(ward_id):
    """
    Get all candidates standing for election in the specified ward.
    
    Args:
        ward_id (str): The ward identifier to search for
        
    Query Parameters:
        candidate_type (str, optional): Filter by candidate type (e.g., 'national', 'provincial', 'local')
        
    Returns:
        JSON array of candidate objects
        
    Example:
        GET /api/v1/wards/12345/candidates
        GET /api/v1/wards/12345/candidates?candidate_type=local
    """
    try:
        # Get candidate_type 
        candidate_type_filter = request.args.get('candidate_type', None)
        
        # Get all distinct candidate types and their locators
        distinct_types_query = """
            SELECT DISTINCT candidate_type, locator FROM candidates
        """
        distinct_types_result = db.session.execute(text(distinct_types_query))
        
        all_candidates = []
        found_ward = False
        
        # Search candidate types by matching ward_id
        for row in distinct_types_result:
            candidate_type = row[0]
            locator = row[1]
            
            # Apply candidate_type filter 
            if candidate_type_filter and candidate_type != candidate_type_filter:
                continue
            
            # Extract the ward code column name from locator
            # locator format: "{code, name}" or "{code}"
            locator_values = locator.strip("{}").split(',')
            ward_code_column = locator_values[0].strip()
            
            # Query candidates for this ward_id in this candidate_type
            retrieve_query = text(f"""
                SELECT * FROM candidates
                WHERE {ward_code_column} = :ward_id
                AND candidate_type = :candidate_type
            """)
            
            params = {'ward_id': ward_id, 'candidate_type': candidate_type}
            result = db.session.execute(retrieve_query, params)
            column_names = result.keys()
            
            for candidate_row in result:
                candidate_dict = dict(zip(column_names, candidate_row))
                all_candidates.append(candidate_dict)
                found_ward = True
        
        # Return results
        if not found_ward:
            return jsonify({
                'ward_id': ward_id,
                'candidates': [],
                'count': 0,
                'message': f'No candidates found for ward_id: {ward_id}'
            }), 200
        
        return jsonify({
            'ward_id': ward_id,
            'candidates': all_candidates,
            'count': len(all_candidates)
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching candidates for ward {ward_id}: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

