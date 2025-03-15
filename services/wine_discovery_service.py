from models import UserPreference, Wine

def get_wine_filters(self):
    """
    Retrieve available wine filters from Elasticsearch
    """
    if not self.es:
        self.logger.error("Elasticsearch not connected")
        return {}

    try:
        # Aggregation query to get unique filter values
        agg_body = {
            "size": 0,
            "aggs": {
                "types": {"terms": {"field": "type"}},
                "regions": {"terms": {"field": "region"}},
                "grape_varieties": {"terms": {"field": "grape_variety"}},
                "traits": {"terms": {"field": "traits"}},
                "price_range": {
                    "range": {
                        "field": "price",
                        "ranges": [
                            {"to": 20},
                            {"from": 20, "to": 50},
                            {"from": 50, "to": 100},
                            {"from": 100}
                        ]
                    }
                }
            }
        }

        results = self.es.search(index=self.index_name, body=agg_body)
        
        # Process aggregation results
        filters = {
            "types": [bucket['key'] for bucket in results['aggregations']['types']['buckets']],
            "regions": [bucket['key'] for bucket in results['aggregations']['regions']['buckets']],
            "grape_varieties": [bucket['key'] for bucket in results['aggregations']['grape_varieties']['buckets']],
            "traits": [bucket['key'] for bucket in results['aggregations']['traits']['buckets']],
            "price_ranges": [
                {
                    "label": self._format_price_range(bucket),
                    "from": bucket.get('from', 0),
                    "to": bucket.get('to', float('inf'))
                } for bucket in results['aggregations']['price_range']['buckets']
            ]
        }

        return filters
    
    except Exception as e:
        self.logger.error(f"Error getting wine filters: {e}")
        return {}

def _format_price_range(self, bucket):
    """
    Format price range label
    """
    if 'from' not in bucket and 'to' in bucket:
        return f"Under ${bucket['to']}"
    elif 'from' in bucket and 'to' in bucket:
        return f"${bucket['from']} - ${bucket['to']}"
    elif 'from' in bucket:
        return f"Over ${bucket['from']}"
    return "Unknown"

def get_wine_suggestions(self, wine_id, user_id=None):
    """
    Enhanced wine suggestions with optional user personalization
    """
    if not self.es:
        self.logger.error("Elasticsearch not connected")
        return {'suggestions': []}

    try:
        wine = Wine.query.get(wine_id)
        
        if not wine:
            self.logger.warning(f"Wine not found: {wine_id}")
            return {'suggestions': []}

        # Base search body for suggestions
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
            "size": 10  # Fetch more suggestions to allow for personalization filtering
        }

        # If user_id is provided, add personalization logic
        if user_id:
            # You might want to implement more sophisticated personalization
            # This is a basic example
            user_preferences = UserPreference.query.filter_by(user_id=user_id).all()
            
            if user_preferences:
                # Add user preference filters
                preference_filters = [
                    {"terms": {field: [pref.value for pref in user_preferences if pref.field == field]}}
                    for field in ['type', 'region', 'grape_variety']
                ]
                
                search_body["query"]["bool"]["should"].extend(preference_filters)
                search_body["query"]["bool"]["minimum_should_match"] = 1

        results = self.es.search(index=self.index_name, body=search_body)
        
        suggestions = [hit['_source'] for hit in results['hits']['hits']]
        
        return {
            'suggestions': suggestions[:5],  # Limit to 5 final suggestions
            'total_suggestions': len(suggestions)
        }
    
    except Exception as e:
        self.logger.error(f"Error getting wine suggestions: {e}")
        return {'suggestions': [], 'total_suggestions': 0}