# services/wine_discovery_service.py
from models import Wine, WineReview, UserInteraction
from extensions import db
from sqlalchemy import func, or_
from elasticsearch import Elasticsearch

class WineDiscoveryService:
    def __init__(self):
        # Initialize Elasticsearch connection
        self.es = Elasticsearch(['localhost:9200'])
        self.index_name = 'wine_discovery'

    def create_wine_index(self):
        """
        Create advanced Elasticsearch index for wine discovery
        """
        index_mapping = {
            "mappings": {
                "properties": {
                    "name": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "type": {"type": "keyword"},
                    "region": {"type": "keyword"},
                    "grape_variety": {"type": "keyword"},
                    "traits": {"type": "keyword"},
                    "price": {"type": "float"},
                    "alcohol_percentage": {"type": "float"},
                    "vintage": {"type": "integer"},
                    "popularity_score": {"type": "float"},
                    "average_rating": {"type": "float"}
                }
            }
        }
        
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=index_mapping)

    def index_wine(self, wine):
        """
        Index wine with advanced metadata
        """
        # Calculate popularity and rating scores
        popularity_score = self._calculate_popularity_score(wine)
        rating_data = self._get_wine_rating(wine.id)

        doc = {
            'name': wine.name,
            'description': wine.description,
            'type': wine.type,
            'region': wine.region,
            'grape_variety': wine.grape_variety,
            'traits': wine.traits.split(',') if wine.traits else [],
            'price': wine.price,
            'alcohol_percentage': wine.alcohol_percentage,
            'vintage': wine.vintage,
            'popularity_score': popularity_score,
            'average_rating': rating_data['average_rating']
        }
        
        self.es.index(index=self.index_name, id=wine.id, body=doc)

    def _calculate_popularity_score(self, wine):
        """
        Calculate wine popularity based on interactions and reviews
        """
        view_count = UserInteraction.query.filter_by(
            wine_id=wine.id, 
            interaction_type='view'
        ).count()
        
        favorite_count = UserInteraction.query.filter_by(
            wine_id=wine.id, 
            interaction_type='favorite'
        ).count()
        
        review_count = WineReview.query.filter_by(wine_id=wine.id).count()
        
        # Weighted calculation
        popularity_score = (
            view_count * 0.3 + 
            favorite_count * 0.5 + 
            review_count * 0.2
        )
        
        return popularity_score

    def _get_wine_rating(self, wine_id):
        """
        Get wine rating details
        """
        rating_data = db.session.query(
            func.avg(WineReview.rating).label('average_rating'),
            func.count(WineReview.id).label('review_count')
        ).filter_by(wine_id=wine_id).first()

        return {
            'average_rating': rating_data.average_rating or 0,
            'review_count': rating_data.review_count or 0
        }

    def advanced_search(self, query_params):
        """
        Advanced wine search with multiple filters
        """
        search_body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "sort": [
                {"popularity_score": {"order": "desc"}},
                {"average_rating": {"order": "desc"}}
            ]
        }

        # Text search
        if query_params.get('query'):
            search_body["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query_params['query'],
                    "fields": [
                        "name^3", 
                        "description^2", 
                        "traits^2"
                    ]
                }
            })

        # Filters
        filters = [
            ('type', 'terms'),
            ('region', 'terms'),
            ('grape_variety', 'terms'),
            ('traits', 'terms')
        ]

        for field, es_type in filters:
            if query_params.get(field):
                search_body["query"]["bool"]["filter"].append({
                    es_type: {field: query_params[field]}
                })

        # Price range filter
        if query_params.get('min_price') or query_params.get('max_price'):
            price_range = {}
            if query_params.get('min_price'):
                price_range['gte'] = query_params['min_price']
            if query_params.get('max_price'):
                price_range['lte'] = query_params['max_price']
            
            search_body["query"]["bool"]["filter"].append({
                "range": {"price": price_range}
            })

        # Execute search
        results = self.es.search(index=self.index_name, body=search_body)
        
        return {
            'total': results['hits']['total']['value'],
            'wines': [hit['_source'] for hit in results['hits']['hits']]
        }

    def get_wine_suggestions(self, wine_id):
        """
        Get wine suggestions based on similarity
        """
        wine = Wine.query.get(wine_id)
        
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"type": wine.type}},
                        {"range": {"price": {
                            "gte": wine.price * 0.8,
                            "lte": wine.price * 1.2
                        }}}
                    ]
                }
            },
            "sort": [
                {"popularity_score": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ],
            "size": 5
        }

        results = self.es.search(index=self.index_name, body=search_body)
        
        return {
            'suggestions': [hit['_source'] for hit in results['hits']['hits']]
        }