import boto3
import os
from botocore.client import Config

def get_spaces_client():
    """
    Create and return a Digital Ocean Spaces client with validation
    """
    # Validate required environment variables
    required_vars = {
        'DO_SPACES_KEY': os.getenv("DO_SPACES_KEY"),
        'DO_SPACES_SECRET': os.getenv("DO_SPACES_SECRET"),
        'DO_SPACES_BUCKET': os.getenv("DO_SPACES_BUCKET"),
        'DO_SPACES_REGION': os.getenv("DO_SPACES_REGION"),
        'DO_SPACES_ENDPOINT': os.getenv("DO_SPACES_ENDPOINT")
    }
    
    missing_vars = [k for k, v in required_vars.items() if not v]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

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