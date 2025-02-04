import boto3
from botocore.client import Config

def get_spaces_client():
    """
    Create and return a Digital Ocean Spaces client with validation
    """
    # Validate required environment variables
    required_vars = {
        'DO_SPACES_KEY': "DO00CDNDXNK3QR2HD7MY",
        'DO_SPACES_SECRET': "E+8VjnUqEtZQS55Buh1hDVOJQFdS7uRbg7FM+4NkBXw",
        'DO_SPACES_BUCKET': "slateai",
        'DO_SPACES_REGION': "lon1",
        'DO_SPACES_ENDPOINT': "https://lon1.digitaloceanspaces.com"
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