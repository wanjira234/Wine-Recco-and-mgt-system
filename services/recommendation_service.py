import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sqlalchemy import create_engine
from models import db, WineReview, Wine, User

class WineRecommendationEngine:
    def __init__(self):
        self.model = None
        self.wine_features = None

    def prepare_collaborative_filtering_data(self):
        # Fetch reviews from database
        reviews_df = pd.read_sql(
            WineReview.query.statement, 
            db.session.bind
        )

        # Prepare data for Surprise library
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            reviews_df[['user_id', 'wine_id', 'rating']], 
            reader
        )

        # Split data
        trainset, testset = train_test_split(data, test_size=0.2)

        # Train SVD model
        self.model = SVD()
        self.model.fit(trainset)

    def content_based_recommendation(self, user_id):
        # Fetch user's past reviews
        user_reviews = WineReview.query.filter_by(user_id=user_id).all()
        
        # Get wine features
        wines = Wine.query.all()
        wine_features = pd.DataFrame([
            {
                'id': wine.id,
                'type': wine.type,
                'region': wine.region,
                'price': wine.price,
                'alcohol_percentage': wine.alcohol_percentage
            } for wine in wines
        ])

        # Encode categorical features
        from sklearn.preprocessing import LabelEncoder
        le_type = LabelEncoder()
        le_region = LabelEncoder()
        
        wine_features['type_encoded'] = le_type.fit_transform(wine_features['type'])
        wine_features['region_encoded'] = le_region.fit_transform(wine_features['region'])

        # Compute similarity
        from sklearn.metrics.pairwise import cosine_similarity
        feature_columns = ['type_encoded', 'region_encoded', 'price', 'alcohol_percentage']
        similarity_matrix = cosine_similarity(wine_features[feature_columns])

        # Find similar wines based on past reviews
        recommended_wines = []
        for review in user_reviews:
            wine_index = wine_features[wine_features['id'] == review.wine_id].index[0]
            similar_indices = similarity_matrix[wine_index].argsort()[::-1][1:6]
            
            recommended_wines.extend(
                wine_features.iloc[similar_indices]['id'].tolist()
            )

        return list(set(recommended_wines))

    def hybrid_recommendation(self, user_id, top_n=10):
        # Collaborative filtering predictions
        collaborative_recs = self._get_collaborative_recommendations(user_id)
        
        # Content-based recommendations
        content_recs = self.content_based_recommendation(user_id)
        
        # Combine and rank recommendations
        combined_recs = collaborative_recs + content_recs
        unique_recs = list(dict.fromkeys(combined_recs))
        
        return unique_recs[:top_n]

    def _get_collaborative_recommendations(self, user_id, top_n=10):
        # Get all wines
        wines = Wine.query.all()
        
        # Predict ratings for unrated wines
        predictions = []
        for wine in wines:
            prediction = self.model.predict(user_id, wine.id)
            predictions.append((wine.id, prediction.est))
        
        # Sort and get top recommendations
        recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)
        return [rec[0] for rec in recommendations[:top_n]]