# blueprints/education.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.education_service import EducationService

education_bp = Blueprint('education', __name__)

@education_bp.route('/recommended-courses', methods=['GET'])
@jwt_required()
def get_recommended_courses():
    """
    Get recommended courses
    """
    user_id = get_jwt_identity()
    difficulty = request.args.get('difficulty')
    
    try:
        courses = EducationService.get_recommended_courses(
            user_id, 
            difficulty
        )
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@education_bp.route('/course/<int:course_id>/start', methods=['POST'])
@jwt_required()
def start_course(course_id):
    """
    Start a new course
    """
    user_id = get_jwt_identity()
    
    try:
        progress = EducationService.start_course(user_id, course_id)
        return jsonify({
            'course_id': progress.course_id,
            'started_at': progress.started_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@education_bp.route('/course/<int:course_id>/module/<int:module_id>/complete', methods=['POST'])
@jwt_required()
def complete_module(course_id, module_id):
    """
    Complete a course module
    """
    user_id = get_jwt_identity()
    
    try:
        progress = EducationService.complete_module(
            user_id, 
            course_id, 
            module_id
        )
        return jsonify({
            'completed_modules': progress.completed_modules,
            'is_course_completed': progress.is_course_completed
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@education_bp.route('/course/<int:course_id>/quiz/<int:quiz_id>', methods=['POST'])
@jwt_required()
def take_quiz(course_id, quiz_id):
    """
    Submit quiz answers
    """
    user_id = get_jwt_identity()
    answers = request.get_json()
    
    try:
        result = EducationService.take_quiz(
            user_id, 
            course_id, 
            quiz_id, 
            answers
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400