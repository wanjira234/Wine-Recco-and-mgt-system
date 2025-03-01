from elasticsearch import Elasticsearch
from models import Wine, UserPreference, UserInteraction
from extensions import db
from sqlalchemy import func

class ElasticsearchService:
    def __init__(self, hosts=['localhost:9200']):
        """
        Initialize Elasticsearch connection
        """
        self.es = Elasticsearch(hosts)
        self.index_name = 'wine_search'

    def create_index(self):
        """
        Create Elasticsearch index with enhanced mapping
        """
        index_mapping = {
            "mappings": {
                "properties": {
                    "name": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "type": {"type": "keyword"},
                    "region": {"type": "keyword"},
                    "price": {"type": "float"},
                    "vintage": {"type": "integer"},
                    "traits": {
                        "type": "keyword",
                        "fields": {
                            "text": {"type": "text"}
                        }
                    },
                    "alcohol_percentage": {"type": "float"}
                }
            }
        }
        
        # Create index if not exists
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=index_mapping)

    def index_wine(self, wine):
        """
        Index a single wine document
        """
        # Split traits if it's a comma-separated string
        traits = wine.traits.split(',') if wine.traits else []

        doc = {
            'name': wine.name,
            'description': wine.description,
            'type': wine.type,
            'region': wine.region,
            'price': wine.price,
            'vintage': wine.vintage,
            'traits': traits,
            'alcohol_percentage': wine.alcohol_percentage
        }
        
        self.es.index(
            index=self.index_name, 
            id=wine.id, 
            body=doc
        )

    def bulk_index_wines(self, wines=None):
        """
        Bulk index wines
        """
        if wines is None:
            wines = Wine.query.all()
        
        actions = []
        for wine in wines:
            # Split traits if it's a comma-separated string
            traits = wine.traits.split(',') if wine.traits else []

            action = {
                "_index": self.index_name,
                "_id": wine.id,
                "_source": {
                    'name': wine.name,
                    'description': wine.description,
                    'type': wine.type,
                    'region': wine.region,
                    'price': wine.price,
                    'vintage': wine.vintage,
                    'traits': traits,
                    'alcohol_percentage': wine.alcohol_percentage
                }
            }
            actions.append(action)
        
        if actions:
            self.es.bulk(body=actions)

    def personalized_search(self, user_id, query=None, filters=None):
        """
        Advanced personalized search considering user preferences and traits
        """
        # Fetch user preferences
        user_preference = UserPreference.query.filter_by(user_id=user_id).first()
        
        # Base search body
        search_body = {
            "query": {
                "bool": {
                    "must": [],
                    "should": [],
                    "filter": []
                }
            },
            "sort": [
                {"_score": {"order": "desc"}},
                {"price": {"order": "asc"}}
            ]
        }

        # Add text query if provided
        if query:
            search_body["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^3", 
                        "description^2", 
                        "region^2", 
                        "traits^2"
                    ]
                }
            })

        # Add user preference-based filtering
        if user_preference:
            # Add preferred traits as boosted should clauses
            if user_preference.preferred_wine_types:
                type_query = {
                    "terms": {
                        "type": user_preference.preferred_wine_types
                    }
                }
                search_body["query"]["bool"]["should"].append(type_query)

        # Add additional filters
        if filters:
            filter_list = []
            for key, value in filters.items():
                if key == 'traits':
                    # Special handling for traits
                    filter_list.append({"terms": {"traits": value}})
                else:
                    filter_list.append({"term": {key: value}})
            
            search_body["query"]["bool"]["filter"].extend(filter_list)

        # Execute search
        results = self.es.search(index=self.index_name, body=search_body)
        
        return {
            'total': results['hits']['total']['value'],
            'wines': [hit['_source'] for hit in results['hits']['hits']],
            'matched_traits': self._extract_matched_traits(results)
        }

    def _extract_matched_traits(self, search_results):
        """
        Extract traits that matched in the search
        """
        matched_traits = set()
        for hit in search_results['hits']['hits']:
            if 'traits' in hit['_source']:
                matched_traits.update(hit['_source']['traits'])
        return list(matched_traits)

    def trait_based_recommendations(self, traits, limit=10):
        """
        Find wines based on specific traits
        """
        search_body = {
            "query": {
                "bool": {
                    "filter": [
                        {"terms": {"traits": traits}}
                    ]
                }
            },
            "size": limit,
            "sort": [
                {"_score": {"order": "desc"}},
                {"price": {"order": "asc"}}
            ]
        }

        results = self.es.search(index=self.index_name, body=search_body)
        
        return {
            'total': results['hits']['total']['value'],
            'wines': [hit['_source'] for hit in results['hits']['hits']]
        }

    def update_wine_traits(self, wine_id, traits):
        """
        Update traits for a specific wine
        """
        # Ensure traits is a list
        if isinstance(traits, str):
            traits = traits.split(',')
        
        # Update wine model
        wine = Wine.query.get(wine_id)
        if wine:
            wine.traits = ','.join(traits)
            db.session.commit()

        # Update Elasticsearch index
        self.es.update(
            index=self.index_name,
            id=wine_id,
            body={
                "doc": {
                    "traits": traits
                }
            }
        )

    def get_all_traits(self):
        """
        Retrieve all unique traits from indexed wines
        """
        search_body = {
            "aggs": {
                "unique_traits": {
                    "terms": {
                        "field": "traits",
                        "size": 100  # Adjust size as needed
                    }
                }
            },
            "size": 0
        }

        results = self.es.search(index=self.index_name, body=search_body)
        
        # Extract trait buckets
        trait_buckets = results['aggregations']['unique_traits']['buckets']
        return [bucket['key'] for bucket in trait_buckets]