import click
from flask.cli import with_appcontext
from services.elasticsearch_service import ElasticsearchService
from models import Wine

@click.command('index-wines')
@with_appcontext
def index_wines_command():
    """
    CLI command to index all wines in Elasticsearch
    """
    es_service = ElasticsearchService()
    
    # Create index if not exists
    es_service.create_index()
    
    # Bulk index all wines
    es_service.bulk_index_wines()
    
    click.echo('Successfully indexed all wines in Elasticsearch')