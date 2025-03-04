# services/search_service.py
from extensions import db
from models import Wine, WineReview
from sqlalchemy import func, or_
from elasticsearch import Elasticsearch
import json

class SearchService:
    def __init__(self):
        # Initialize Elasticsearch connection
        self.es = Elasticsearch(['http://localhost:9200'])
        self.index_name = 'wine_index'

    def index_wines(self):
        """
        Index wines in Elasticsearch for advanced search
        """
        # Fetch all wines
        wines = Wine.query.all()
        
        for wine in wines:
            # Prepare wine document for indexing
            wine_doc = {
                'id': wine.id,
                'name': wine.name,
                'type': wine.type,
                'region': wine.region,
                'description': wine.description,
                'price': wine.price,
                'alcohol_percentage': wine.alcohol_percentage,
                'traits': wine.traits or [],
                'average_rating': self._calculate_average_rating(wine),
                'review_count': len(wine.reviews)
            }
            
            # Index document
            self.es.index(
                index=self.index_name, 
                id=wine.id, 
                body=wine_doc
            )
        
        # Refresh index
        self.es.indices.refresh(index=self.index_name)

    def _calculate_average_rating(self, wine):
        """
        Calculate average rating for a wine
        """
        ratings = [review.rating for review in wine.reviews]
        return sum(ratings) / len(ratings) if ratings else 0

    def advanced_search(self, query_params):
        """
        Perform advanced search with multiple filters
        """
        # Prepare Elasticsearch query
        es_query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "sort": [],
            "aggs": {
                "wine_types": {"terms": {"field": "type.keyword"}},
                "price_ranges": {
                    "range": {
                        "field": "price",
                        "ranges": [
                            {"to": 20, "key": "Budget"},
                            {"from": 20, "to": 50, "key": "Mid-Range"},
                            {"from": 50, "to": 100, "key": "Premium"},
                            {"from": 100, "key": "Luxury"}
                        ]
                    }
                }
            }
        }

        # Text search
        if query_params.get('q'):
            es_query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query_params['q'],
                    "fields": [
                        "name^3", 
                        "description^2", 
                        "region", 
                        "traits"
                    ]
                }
            })

        # Wine type filter
        if query_params.get('type'):
            es_query["query"]["bool"]["filter"].append({
                "term": {"type.keyword": query_params['type']}
            })

        # Price range filter
        if query_params.get('price_min'):
            es_query["query"]["bool"]["filter"].append({
                "range": {"price": {"gte": query_params['price_min']}}
            })
        if query_params.get('price_max'):
            es_query["query"]["bool"]["filter"].append({
                "range": {"price": {"lte": query_params['price_max']}}
            })

        # Traits filter
        if query_params.get('traits'):
            traits = query_params['traits'].split(',')
            es_query["query"]["bool"]["filter"].append({
                "terms": {"traits.keyword": traits}
            })

        # Sorting
        if query_params.get('sort'):
            sort_mapping = {
                'price_asc': {"price": {"order": "asc"}},
                'price_desc': {"price": {"order": "desc"}},
                'rating': {"average_rating": {"order": "desc"}},
                'popularity': {"review_count": {"order": "desc"}}
            }
            es_query["sort"].append(sort_mapping.get(query_params['sort'], {}))

        # Pagination
        page = query_params.get('page', 1)
        per_page = query_params.get('per_page', 20)
        from_record = (page - 1) * per_page

        # Execute search
        results = self.es.search(
            index=self.index_name,
            body=es_query,
            from_=from_record,
            size=per_page
        )

        # Process results
        return {
            'wines': [hit['_source'] for hit in results['hits']['hits']],
            'total': results['hits']['total']['value'],
            'aggregations': {
                'wine_types': results['aggregations']['wine_types']['buckets'],
                'price_ranges': results['aggregations']['price_ranges']['buckets']
            },
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': (results['hits']['total']['value'] + per_page - 1) // per_page
            }
        }

    def suggest_wines(self, query):
        """
        Provide wine suggestions based on partial input
        """
        suggest_query = {
            "suggest": {
                "wine-suggest": {
                    "prefix": query,
                    "completion": {
                        "field": "name.suggest"
                    }
                }
            }
        }

        results = self.es.search(
            index=self.index_name,
            body=suggest_query
        )

        return [
            suggestion['text'] 
            for suggestion in results['suggest']['wine-suggest'][0]['options']
        ]