from flask import current_app
from models import Wine, WineReview, UserInteraction, UserPreference
from extensions import db
from sqlalchemy import func, or_
from elasticsearch import Elasticsearch
import logging
import os

class WineDiscoveryService:
    _instance = None

    def __new__(cls):
        """
        Singleton pattern to ensure only one instance
        """
        if not cls._instance:
            cls._instance = super(WineDiscoveryService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize service with lazy loading
        """
        if not hasattr(self, 'initialized'):
            # Logging setup
            self.logger = logging.getLogger(__name__)
            
            # Elasticsearch configuration
            self.es_host = os.getenv(
                'ELASTICSEARCH_HOST', 
                'http://localhost:9200'
            )
            
            # Defer Elasticsearch connection
            self.es = None
            self.index_name = 'wine_discovery'
            
            # Initialization flag
            self.initialized = False

    def connect(self, app=None):
        """
        Establish Elasticsearch connection
        
        :param app: Flask application context (optional)
        :return: Elasticsearch client
        """
        try:
            # Use app config if provided
            if app:
                es_host = app.config.get('ELASTICSEARCH_HOST', self.es_host)
                index_name = app.config.get(
                    'ELASTICSEARCH_WINE_INDEX', 
                    'wine_discovery'
                )
            else:
                es_host = self.es_host
                index_name = self.index_name

            # Configure Elasticsearch connection
            self.es = Elasticsearch(
                [es_host],
                retry_on_timeout=True,
                max_retries=3,
                timeout=30
            )
            
            # Verify connection
            if not self.es.ping():
                raise ValueError("Elasticsearch connection failed")
            
            # Set index name
            self.index_name = index_name
            
            # Mark as initialized
            self.initialized = True
            
            self.logger.info("Elasticsearch connected successfully")
            return self.es
        
        except Exception as e:
            self.logger.error(f"Elasticsearch connection error: {e}")
            self.es = None
            self.initialized = False
            return None

    def initialize_service(self, app=None):
        """
        Public method to initialize the service
        
        :param app: Flask application context
        :return: Initialized service instance
        """
        if not self.initialized:
            self.connect(app)
        return self

    # Rest of the methods from previous implementation...

    def advanced_search(self, query_params):
        """
        Advanced wine search with multiple filters and error handling
        """
        if not self.es:
            self.logger.error("Elasticsearch not connected")
            return {'total': 0, 'wines': []}

        try:
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
                ],
                "from": (query_params.get('page', 1) - 1) * query_params.get('per_page', 20),
                "size": query_params.get('per_page', 20)
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
        
        except Exception as e:
            self.logger.error(f"Error in advanced search: {e}")
            return {'total': 0, 'wines': []}

# Global function to create service
def create_wine_discovery_service(app=None):
    """
    Create and initialize WineDiscoveryService
    
    :param app: Flask application context
    :return: Initialized WineDiscoveryService instance
    """
    service = WineDiscoveryService()
    
    # Initialize with app context if provided
    if app:
        with app.app_context():
            service.initialize_service(app)
    
    return service

# Global service instance
wine_discovery_service = WineDiscoveryService()