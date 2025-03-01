# services/analytics_service.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from extensions import db
from models import Wine, WineReview, UserInteraction, UserPreference
from sqlalchemy import func, distinct

class AnalyticsService:
    def __init__(self):
        self.prepare_wine_dataset()

    def prepare_wine_dataset(self):
        """
        Prepare comprehensive wine dataset for analysis
        """
        # Fetch wine data with aggregated metrics
        wines = db.session.query(
            Wine,
            func.avg(WineReview.rating).label('avg_rating'),
            func.count(WineReview.id).label('review_count'),
            func.count(distinct(UserInteraction.user_id)).label('unique_views')
        ).outerjoin(WineReview, Wine.id == WineReview.wine_id) \
         .outerjoin(UserInteraction, Wine.id == UserInteraction.wine_id) \
         .group_by(Wine.id).all()

        # Convert to DataFrame
        self.wine_df = pd.DataFrame([
            {
                'id': wine.Wine.id,
                'name': wine.Wine.name,
                'price': wine.Wine.price,
                'alcohol_percentage': wine.Wine.alcohol_percentage,
                'type': wine.Wine.type,
                'avg_rating': wine.avg_rating or 0,
                'review_count': wine.review_count,
                'unique_views': wine.unique_views
            } for wine in wines
        ])

    def wine_clustering(self, n_clusters=5):
        """
        Perform wine clustering using K-Means
        """
        # Prepare features for clustering
        features = ['price', 'alcohol_percentage', 'avg_rating', 'review_count']
        
        # Normalize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(self.wine_df[features])
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.wine_df['cluster'] = kmeans.fit_predict(scaled_features)
        
        # Analyze cluster characteristics
        cluster_analysis = self.wine_df.groupby('cluster')[features].mean()
        
        return {
            'cluster_centers': cluster_analysis.to_dict(),
            'wines_per_cluster': self.wine_df['cluster'].value_counts().to_dict()
        }

    def wine_recommendation_insights(self):
        """
        Generate wine recommendation insights
        """
        # Analyze wine types popularity
        type_popularity = db.session.query(
            Wine.type, 
            func.count(Wine.id).label('wine_count'),
            func.avg(WineReview.rating).label('avg_rating')
        ).outerjoin(WineReview, Wine.id == WineReview.wine_id) \
         .group_by(Wine.type).all()

        # User preference analysis
        user_preferences = db.session.query(
            UserPreference.preferred_wine_types,
            func.count(UserPreference.user_id).label('user_count')
        ).group_by(UserPreference.preferred_wine_types).all()

        return {
            'wine_type_popularity': [
                {
                    'type': result.type,
                    'wine_count': result.wine_count,
                    'avg_rating': float(result.avg_rating or 0)
                } for result in type_popularity
            ],
            'user_preferences': [
                {
                    'wine_types': result.preferred_wine_types,
                    'user_count': result.user_count
                } for result in user_preferences
            ]
        }

    def price_sensitivity_analysis(self):
        """
        Analyze price sensitivity and its impact on ratings
        """
        # Bin prices and calculate average ratings
        self.wine_df['price_bin'] = pd.cut(
            self.wine_df['price'], 
            bins=[0, 20, 50, 100, 200, float('inf')],
            labels=['Budget', 'Affordable', 'Mid-range', 'Premium', 'Luxury']
        )

        price_sensitivity = self.wine_df.groupby('price_bin').agg({
            'avg_rating': 'mean',
            'review_count': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'wine_count'})

        return price_sensitivity.to_dict(orient='index')

    def predictive_wine_rating(self):
        """
        Build a predictive model for wine ratings
        """
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestRegressor
        
        # Prepare features
        features = ['price', 'alcohol_percentage', 'review_count']
        X = self.wine_df[features]
        y = self.wine_df['avg_rating']

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train Random Forest Regressor
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        # Model evaluation
        train_score = rf_model.score(X_train, y_train)
        test_score = rf_model.score(X_test, y_test)

        # Feature importance
        feature_importance = dict(zip(features, rf_model.feature_importances_))

        return {
            'train_score': train_score,
            'test_score': test_score,
            'feature_importance': feature_importance
        }

    def generate_comprehensive_report(self):
        """
        Generate a comprehensive analytics report
        """
        return {
            'clustering_insights': self.wine_clustering(),
            'recommendation_insights': self.wine_recommendation_insights(),
            'price_sensitivity': self.price_sensitivity_analysis(),
            'rating_prediction': self.predictive_wine_rating()
        }