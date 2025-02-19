import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from flask_login import current_user
from models import db, WineReview, Wine, User

class WineRecommendationService:
    def __init__(self):
        self.collaborative_model = None
        self.wine_features = None
        self.similarity_matrix = None

    def prepare_recommendation_data(self):
        """
        Prepare recommendation data using collaborative and content-based approaches
        """
        try:
            # Fetch reviews data
            reviews_df = self._fetch_reviews_dataframe()
            
            # Prepare collaborative filtering model
            self._prepare_collaborative_model(reviews_df)
            
            # Prepare content-based features
            self._prepare_wine_features()
            
            print("Recommendation engine initialized successfully")
        except Exception as e:
            print(f"Error initializing recommendation engine: {str(e)}")

    def _fetch_reviews_dataframe(self):
        """
        Fetch wine reviews and convert to DataFrame
        """
        reviews = WineReview.query.all()
        reviews_data = [
            {
                'user_id': review.user_id, 
                'wine_id': review.wine_id, 
                'rating': review.rating
            } for review in reviews
        ]
        return pd.DataFrame(reviews_data)

    def _prepare_collaborative_model(self, reviews_df):
        """
        Train collaborative filtering model using SVD
        """
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            reviews_df[['user_id', 'wine_id', 'rating']], 
            reader
        )

        # Split data
        trainset, _ = train_test_split(data, test_size=0.2)

        # Train SVD model
        self.collaborative_model = SVD()
        self.collaborative_model.fit(trainset)

    def _prepare_wine_features(self):
        """
        Prepare wine features for content-based filtering
        """
        # Get all wines
        wines = Wine.query.all()
        
        # Create DataFrame with wine features
        wine_features = pd.DataFrame([
            {
                'id': wine.id,
                'type': wine.type,
                'region': wine.region,
                'price': wine.price,
                'alcohol_percentage': wine.alcohol_percentage or 0
            } for wine in wines
        ])

        # Encode categorical features
        le_type = LabelEncoder()
        le_region = LabelEncoder()
        
        wine_features['type_encoded'] = le_type.fit_transform(wine_features['type'])
        wine_features['region_encoded'] = le_region.fit_transform(wine_features['region'])

        # Compute similarity matrix
        feature_columns = ['type_encoded', 'region_encoded', 'price', 'alcohol_percentage']
        self.similarity_matrix = cosine_similarity(wine_features[feature_columns])
        self.wine_features = wine_features

    def content_based_recommendation(self, user_id, top_n=10):
        """
        Generate content-based recommendations
        """
        # Fetch user's past reviews
        user_reviews = WineReview.query.filter_by(user_id=user_id).all()
        
        if not user_reviews or self.wine_features is None:
            # If no reviews or features not prepared, return random recommendations
            return Wine.query.order_by(db.func.random()).limit(top_n).all()

        recommended_wine_ids = []
        for review in user_reviews:
            wine_index = self.wine_features[self.wine_features['id'] == review.wine_id].index[0]
            similar_indices = self.similarity_matrix[wine_index].argsort()[::-1][1:6]
            
            recommended_wine_ids.extend(
                self.wine_features.iloc[similar_indices]['id'].tolist()
            )

        return list(set(recommended_wine_ids))[:top_n]

    def collaborative_recommendations(self, user_id, top_n=10):
        """
        Generate collaborative filtering recommendations
        """
        if self.collaborative_model is None:
            return []

        # Get all wines
        wines = Wine.query.all()
        
        # Predict ratings for unrated wines
        predictions = []
        for wine in wines:
            prediction = self.collaborative_model.predict(user_id, wine.id)
            predictions.append((wine.id, prediction.est))
        
        # Sort and get top recommendations
        recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)
        return [rec[0] for rec in recommendations[:top_n]]

    def hybrid_recommendation(self, user_id, top_n=10):
        """
        Generate hybrid recommendations combining collaborative and content-based approaches
        """
        # Collaborative filtering predictions
        collaborative_recs = self.collaborative_recommendations(user_id)
        
        # Content-based recommendations
        content_recs = self.content_based_recommendation(user_id)
        
        # Combine and rank recommendations
        combined_recs = collaborative_recs + content_recs
        unique_recs = list(dict.fromkeys(combined_recs))
        
        return unique_recs[:top_n]

# Create a singleton instance of the recommendation service
recommendation_engine = WineRecommendationService()