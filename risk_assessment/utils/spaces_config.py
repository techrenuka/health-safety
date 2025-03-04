import boto3
from botocore.client import Config
from django.conf import settings

def get_spaces_client():
    """
    Create and return a Digital Ocean Spaces client with validation
    """
    # Validate required settings
    required_vars = {
        'DO_SPACES_KEY': settings.DO_SPACES_KEY,
        'DO_SPACES_SECRET': settings.DO_SPACES_SECRET,
        'DO_SPACES_BUCKET': settings.DO_SPACES_BUCKET,
        'DO_SPACES_REGION': settings.DO_SPACES_REGION,
        'DO_SPACES_ENDPOINT': settings.DO_SPACES_ENDPOINT
    }
    
    missing_vars = [k for k, v in required_vars.items() if not v]
    if missing_vars:
        raise ValueError(f"Missing required settings: {', '.join(missing_vars)}")

    try:
        session = boto3.session.Session()
        client = session.client('s3',
            region_name=required_vars['DO_SPACES_REGION'],
            endpoint_url=required_vars['DO_SPACES_ENDPOINT'],
            aws_access_key_id=required_vars['DO_SPACES_KEY'],
            aws_secret_access_key=required_vars['DO_SPACES_SECRET'],
            config=Config(s3={'addressing_style': 'virtual'}),
        )
        
        # Test connection by listing buckets
        client.list_buckets()
        
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Digital Ocean Spaces: {str(e)}")