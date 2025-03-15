import numpy as np
import pandas as pd
import pickle
import os
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from extensions import db
from models import Wine, UserPreference, WineReview

class RecommendationEngine:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(RecommendationEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self, data_folder='./data'):
        if not hasattr(self, 'initialized'):
            self.data_folder = data_folder
            os.makedirs(data_folder, exist_ok=True)
            self.initialized = False
            self.wine_df = None
            self.tfidf_matrix = None

    def initialize(self):
        """
        Lazy initialization method with application context handling
        """
        from flask import current_app
        
        try:
            # Ensure we're in an application context
            with current_app.app_context():
                self.load_wine_data()
                self.initialized = True
                print("Recommendation engine initialized successfully")
        except Exception as e:
            print(f"Failed to initialize recommendation engine: {e}")
            self.initialized = False

    def load_wine_data(self):
        """
        Load wine data from database and prepare for recommendations
        Must be called within an application context
        """
        # Fetch all wines
        wines = Wine.query.all()
        
        # Convert wines to DataFrame
        self.wine_df = pd.DataFrame([
            {
                'id': wine.id,
                'name': wine.name,
                'type': wine.type,
                'region': wine.region,
                'description': wine.description or '',
                'price': wine.price,
                'avg_rating': self._calculate_average_rating(wine)
            } for wine in wines
        ])
        
        # Prepare TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = tfidf_vectorizer.fit_transform(
            self.wine_df['description'].fillna('')
        )

    def extract_wine_traits(self):
        """
        Extract unique traits from wines
        """
        # Collect all traits from wines
        all_traits_set = set()
        for traits_str in self.wine_df['traits'].dropna():
            if isinstance(traits_str, str):
                traits = [trait.strip() for trait in traits_str.split(',')]
                all_traits_set.update(traits)
        
        self.all_traits = list(all_traits_set)

    def _calculate_average_rating(self, wine):
        """
        Calculate average rating for a wine
        """
        reviews = WineReview.query.filter_by(wine_id=wine.id).all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

    def recommend_by_traits(self, selected_traits=None, top_n=10):
        """
        Recommend wines based on selected traits
        
        :param selected_traits: List of traits to filter by
        :param top_n: Number of recommendations to return
        :return: DataFrame of recommended wines
        """
        if not self.initialized:
            self.initialize()

        # If no traits specified, return popular wines
        if not selected_traits:
            return self.wine_df.nlargest(top_n, 'avg_rating')

        # Filter wines that match the selected traits
        def traits_match(wine_traits):
            if not isinstance(wine_traits, str):
                return False
            wine_trait_list = [trait.strip() for trait in wine_traits.split(',')]
            return any(trait in wine_trait_list for trait in selected_traits)

        trait_matched_wines = self.wine_df[
            self.wine_df['traits'].apply(traits_match)
        ]

        # If no wines match, return popular wines
        if trait_matched_wines.empty:
            return self.wine_df.nlargest(top_n, 'avg_rating')

        # Sort by average rating and return top N
        return trait_matched_wines.nlargest(top_n, 'avg_rating')

    def hybrid_recommendations(self, user_id, top_n=5):
        """
        Generate hybrid recommendations
        """
        if not self.initialized:
            self.initialize()

        # Get user's past reviews
        user_reviews = WineReview.query.filter_by(user_id=user_id).all()
        
        if not user_reviews:
            return self._get_popular_wines(top_n)
        
        # Get liked wines
        liked_wine_ids = [review.wine_id for review in user_reviews if review.rating >= 4]
        
        if not liked_wine_ids:
            return self._get_popular_wines(top_n)
        
        # Generate recommendations
        recommended_wines = []
        for wine_id in liked_wine_ids:
            content_based_recs = self._content_based_recommendations(wine_id)
            recommended_wines.extend(content_based_recs)
        
        # Remove duplicates and already reviewed wines
        recommended_wines = list(set(recommended_wines))
        recommended_wines = [
            wine_id for wine_id in recommended_wines 
            if wine_id not in [review.wine_id for review in user_reviews]
        ]
        
        return recommended_wines[:top_n]

    def _content_based_recommendations(self, wine_id, top_n=5):
        """
        Generate content-based recommendations
        """
        wine_index = self.wine_df[self.wine_df['id'] == wine_id].index[0]
        
        similarity_scores = cosine_similarity(
            self.tfidf_matrix[wine_index], 
            self.tfidf_matrix
        ).flatten()
        
        similar_indices = similarity_scores.argsort()[::-1][1:top_n+1]
        
        return self.wine_df.iloc[similar_indices]['id'].tolist()

    def _get_popular_wines(self, top_n=5):
        """
        Get most popular wines
        """
        popular_wines = self.wine_df.nlargest(top_n, 'avg_rating')
        return popular_wines['id'].tolist()

# Global instance
recommendation_engine = RecommendationEngine()