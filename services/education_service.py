# services/education_service.py
from extensions import db
from models import (
    WineCourse, 
    CourseModule, 
    CourseQuiz, 
    QuizQuestion, 
    UserCourseProgress,
    CourseCategory
)
from services.subscription_service import SubscriptionService
import random

class EducationService:
    @classmethod
    def get_recommended_courses(cls, user_id, difficulty=None):
        """
        Get recommended courses based on user's learning history
        """
        # Check user's subscription tier for course access
        if not SubscriptionService.check_subscription_access(
            user_id, 
            required_tier='PREMIUM'
        ):
            return []

        # Get user's completed courses and progress
        completed_courses = UserCourseProgress.query.filter_by(
            user_id=user_id, 
            is_course_completed=True
        ).all()

        # Determine recommended difficulty
        if not difficulty:
            if not completed_courses:
                difficulty = CourseCategory.BEGINNER
            else:
                # Suggest next difficulty level
                difficulty = cls._get_next_difficulty(completed_courses)

        # Find recommended courses
        recommended = WineCourse.query.filter_by(category=difficulty).all()
        
        return [
            {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'category': course.category.value,
                'course_type': course.course_type.value,
                'duration_minutes': course.duration_minutes,
                'thumbnail_url': course.thumbnail_url
            } for course in recommended
        ]

    @classmethod
    def _get_next_difficulty(cls, completed_courses):
        """
        Determine next difficulty level based on completed courses
        """
        difficulty_order = [
            CourseCategory.BEGINNER, 
            CourseCategory.INTERMEDIATE, 
            CourseCategory.ADVANCED, 
            CourseCategory.SOMMELIER
        ]
        
        # Find highest completed difficulty
        highest_difficulty = max(
            [difficulty_order.index(
                CourseCategory(course.course.category)
            ) for course in completed_courses]
        )
        
        # Return next difficulty or max if at top
        return difficulty_order[
            min(highest_difficulty + 1, len(difficulty_order) - 1)
        ]

    @classmethod
    def start_course(cls, user_id, course_id):
        """
        Start a new course for a user
        """
        # Check if course progress already exists
        existing_progress = UserCourseProgress.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()
        
        if existing_progress:
            return existing_progress
        
        # Create new course progress
        progress = UserCourseProgress(
            user_id=user_id,
            course_id=course_id
        )
        
        db.session.add(progress)
        db.session.commit()
        
        return progress

    @classmethod
    def complete_module(cls, user_id, course_id, module_id):
        """
        Mark a module as completed
        """
        progress = UserCourseProgress.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()
        
        if not progress:
            raise ValueError("Course not started")
        
        # Update completed modules
        completed_modules = progress.completed_modules or []
        if module_id not in completed_modules:
            completed_modules.append(module_id)
        
        progress.completed_modules = completed_modules
        
        # Check if all modules are completed
        course_modules = CourseModule.query.filter_by(course_id=course_id).count()
        if len(completed_modules) == course_modules:
            progress.is_course_completed = True
            progress.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return progress

    @classmethod
    def take_quiz(cls, user_id, course_id, quiz_id, answers):
        """
        Process quiz submission
        """
        # Get quiz and questions
        quiz = CourseQuiz.query.get(quiz_id)
        
        if not quiz or quiz.course_id != course_id:
            raise ValueError("Invalid quiz")
        
        # Calculate score
        total_questions = len(quiz.questions)
        correct_answers = 0
        
        for question in quiz.questions:
            user_answer = answers.get(str(question.id))
            if user_answer == question.correct_answer:
                correct_answers += 1
        
        # Calculate percentage
        score = correct_answers / total_questions
        
        # Update user progress
        progress = UserCourseProgress.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()
        
        if progress:
            progress.quiz_attempts += 1
            progress.highest_quiz_score = max(
                progress.highest_quiz_score or 0, 
                score
            )
            
            # Mark course as completed if passed
            if score >= quiz.passing_score:
                progress.is_course_completed = True
                progress.completed_at = datetime.utcnow()
            
            db.session.commit()
        
        return {
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'passed': score >= quiz.passing_score
        }