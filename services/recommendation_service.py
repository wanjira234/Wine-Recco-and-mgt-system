import numpy as np
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Dataset, Reader, KNNBaseline
from extensions import db
from models import Wine, UserPreference, WineReview
from sqlalchemy import func
import os

class RecommendationEngine:
    def __init__(self, data_folder='./data'):
        # Load pre-trained models and dataframes
        self.df_wine_model = pd.read_pickle(os.path.join(data_folder, 'df_wine_us_rate.pkl'))
        self.df_wine_combi = pd.read_pickle(os.path.join(data_folder, 'df_wine_combi.pkl'))
        
        # Predefined traits list
        self.all_traits =[
              'almond', 'anise', 'apple', 'apricot', 'baked', 'baking_spices', 'berry', 'black_cherry', 'black_currant', 'black_pepper', 'black_tea', 'blackberry', 'blueberry', 
              'boysenberry', 'bramble', 'bright', 'butter', 'candy', 'caramel', 'cardamom', 'cassis', 'cedar', 'chalk', 'cherry', 'chocolate', 'cinnamon', 'citrus', 'clean', 'closed',
              'clove', 'cocoa', 'coffee', 'cola', 'complex', 'concentrated', 'cranberry', 'cream', 'crisp', 'dark', 'dark_chocolate', 'dense', 'depth', 'dried_herb', 'dry', 'dust',
              'earth', 'edgy', 'elderberry', 'elegant', 'fennel', 'firm', 'flower', 'forest_floor', 'french_oak', 'fresh', 'fruit', 'full_bodied', 'game', 'grapefruit', 'graphite',
              'green', 'gripping', 'grippy', 'hearty', 'herb', 'honey', 'honeysuckle', 'jam', 'juicy', 'lavender', 'leafy', 'lean', 'leather', 'lemon', 'lemon_peel', 'length', 'licorice',
              'light_bodied', 'lime', 'lush', 'meaty', 'medium_bodied', 'melon', 'milk_chocolate', 'minerality', 'mint', 'nutmeg', 'oak', 'olive', 'orange', 'orange_peel', 'peach',
              'pear', 'pencil_lead', 'pepper', 'pine', 'pineapple', 'plum', 'plush', 'polished', 'pomegranate', 'powerful', 'purple', 'purple_flower', 'raspberry', 'refreshing',
              'restrained', 'rich', 'ripe', 'robust', 'rose', 'round', 'sage', 'salt', 'savory', 'sharp', 'silky', 'smoke', 'smoked_meat', 'smooth', 'soft', 'sparkling', 'spice',
              'steel', 'stone', 'strawberry', 'succulent', 'supple', 'sweet', 'tangy', 'tannin', 'tar', 'tart', 'tea', 'thick', 'thyme', 'tight', 'toast', 'tobacco', 'tropical_fruit',
              'vanilla', 'velvety', 'vibrant', 'violet', 'warm', 'weight', 'wet_rocks', 'white', 'white_pepper', 'wood']
        
        # Load or initialize recommendation model
        self.load_recommendation_model()
        
        # Load wine data for content-based recommendations
        self.load_wine_data()

    def load_recommendation_model(self):
        """
        Load or train the KNN recommendation model
        """
        # Instantiate reader & data for surprise
        reader = Reader(rating_scale=(88, 100))
        data = Dataset.load_from_df(self.df_wine_model, reader)
        
        # Instantiate recsys model
        sim_options = {'name': 'cosine'}
        self.model = KNNBaseline(k=35, min_k=1, sim_options=sim_options, verbose=False)

        # Train & fit the data into model
        train = data.build_full_trainset()
        self.model.fit(train)

    def load_wine_data(self):
        """
        Load wine data for content-based recommendations
        """
        # Prepare DataFrame for content-based filtering
        self.wine_df = pd.DataFrame([
            {
                'id': wine.id,
                'name': wine.name,
                'description': wine.description,
                'type': wine.type,
                'region': wine.region,
                'price': wine.price,
                'traits': wine.traits if wine.traits else ''
            } for wine in Wine.query.all()
        ])

        # Prepare TF-IDF vectorization
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(
            self.wine_df['description'] + ' ' + 
            self.wine_df['traits'] + ' ' + 
            self.wine_df['type'] + ' ' + 
            self.wine_df['region']
        )

    def recommend_by_traits(self, selected_traits=None, top_n=10):
        """
        Recommend wines based on selected traits
        """
        # Use all traits if none selected
        if not selected_traits:
            selected_traits = self.all_traits

        # Prepare traits filter
        trait_filter = ['title']
        trait_filter.extend(selected_traits)

        # Create dataframe for wine name and traits
        df_temp_traits = self.df_wine_combi.drop(columns=[
            'taster_name', 'points', 'variety', 'designation', 'winery', 
            'country', 'province', 'region_1', 'region_2', 'price', 
            'description', 'desc_wd_count', 'traits'
        ])

        # Filter wines with selected traits
        df_temp_traits = df_temp_traits[trait_filter]
        df_temp_traits['sum'] = df_temp_traits.sum(axis=1, numeric_only=True)
        df_temp_traits = df_temp_traits[df_temp_traits['sum'] != 0]

        # Get recommendation scores
        recommend_df = self._get_recommendation_scores()

        # Merge selected wines traits with recommend scores
        df_selectrec_temp = df_temp_traits.merge(recommend_df, on='title', how='left')

        # Merge with full details
        df_selectrec_detail = df_selectrec_temp.merge(
            self.df_wine_combi, on='title', how='left'
        )
        df_selectrec_detail.drop_duplicates(inplace=True)

        # Get top recommendations
        df_rec_raw = df_selectrec_detail.sort_values(
            'est_match_pts', ascending=False
        ).head(top_n)

        return df_rec_raw

    def _get_recommendation_scores(self):
        """
        Compute recommendation scores using the pre-trained model
        """
        recommend_list = []
        user_wines = self.df_wine_model[
            self.df_wine_model.taster_name == 'mockuser'
        ]['title'].unique()
        
        not_user_wines = [
            wine for wine in self.df_wine_model['title'].unique() 
            if wine not in user_wines
        ]

        for wine in not_user_wines:
            prediction = self.model.predict(uid='mockuser', iid=wine)
            recommend_list.append([prediction.iid, prediction.est])
        
        return pd.DataFrame(recommend_list, columns=['title', 'est_match_pts'])

    def content_based_recommendations(self, wine_id, top_n=5):
        """
        Generate recommendations based on wine content similarity
        """
        # Find the index of the wine
        wine_index = self.wine_df[self.wine_df['id'] == wine_id].index[0]
        
        # Calculate cosine similarity
        cosine_similarities = cosine_similarity(
            self.tfidf_matrix[wine_index], 
            self.tfidf_matrix
        ).flatten()
        
        # Get top similar wines (excluding the input wine)
        similar_indices = cosine_similarities.argsort()[::-1][1:top_n+1]
        
        return self.wine_df.iloc[similar_indices]['id'].tolist()

    def hybrid_recommendations(self, user_id, wine_id=None, top_n=5):
        """
        Generate hybrid recommendations combining multiple approaches
        """
        # Get user preferences
        user_preference = UserPreference.query.filter_by(user_id=user_id).first()
        
        # Combine recommendation strategies
        recommendations = set()
        
        # Content-based recommendations if wine_id provided
        if wine_id:
            content_recs = self.content_based_recommendations(wine_id, top_n)
            recommendations.update(content_recs)
        
        # Collaborative filtering recommendations
        collab_recs = self._get_collaborative_recommendations(user_id, top_n)
        recommendations.update(collab_recs)
        
        # Filter recommendations based on user preferences
        if user_preference:
            filtered_recs = self._filter_by_preferences(
                list(recommendations), 
                user_preference
            )
        else:
            filtered_recs = list(recommendations)
        
        # Ensure unique recommendations
        return list(dict.fromkeys(filtered_recs))[:top_n]

    def _get_collaborative_recommendations(self, user_id, top_n=5):
        """
        Get collaborative filtering recommendations
        """
        # Fetch user's past interactions
        user_interactions = WineReview.query.filter_by(user_id=user_id).all()
        
        if not user_interactions:
            return self._get_trending_wines(top_n)
        
        # Use the pre-trained model to get recommendations
        recommend_df = self._get_recommendation_scores()
        
        # Convert to list of wine IDs
        wine_titles = recommend_df.sort_values(
            'est_match_pts', ascending=False
        )['title'].head(top_n).tolist()
        
        # Map wine titles to wine IDs
        recommended_wines = Wine.query.filter(
            Wine.name.in_(wine_titles)
        ).all()
        
        return [wine.id for wine in recommended_wines]

    def _filter_by_preferences(self, recommendations, user_preference):
        """
        Filter recommendations based on user preferences
        """
        filtered_wines = []
        
        for wine_id in recommendations:
            wine = Wine.query.get(wine_id)
            
            # Check preference criteria
            if (not user_preference.preferred_wine_types or 
                wine.type in user_preference.preferred_wine_types) and \
               (not user_preference.preferred_price_range or 
                (user_preference.preferred_price_range[0] <= wine.price <= 
                 user_preference.preferred_price_range[1])):
                filtered_wines.append(wine_id)
        
        return filtered_wines

    def _get_trending_wines(self, top_n=5):
        """
        Get trending wines based on recent purchases and reviews
        """
        trending_wines = db.session.query(
            WineReview.wine_id, 
            func.count(WineReview.id).label('review_count')
        ).group_by(WineReview.wine_id).order_by(
            func.count(WineReview.id).desc()
        ).limit(top_n).all()
        
        return [wine_id for wine_id, _ in trending_wines]