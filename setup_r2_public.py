#!/usr/bin/env python
"""
Script to setup R2 bucket for public access
"""
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def setup_r2_public_access():
    """Setup R2 bucket for public access"""
    
    # Create S3 client for R2
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv('R2_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
    )
    
    bucket_name = os.getenv('R2_BUCKET_NAME')
    
    try:
        # Set bucket policy for public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        
        # Apply bucket policy
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=str(bucket_policy).replace("'", '"')
        )
        
        print("✅ Bucket policy set for public read access")
        
        # Set CORS configuration
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'HEAD'],
                    'AllowedOrigins': ['*'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        
        print("✅ CORS configuration set")
        
        # Test public access
        test_file = "test_public_access.txt"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_file,
            Body=b"Test public access",
            ACL='public-read'
        )
        
        print(f"✅ Test file uploaded: {test_file}")
        
        # Get public URL
        public_url = f"https://pub-e4286a7e2c854dd2b75a10748857903a.r2.dev/{test_file}"
        print(f"🌐 Test URL: {public_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up public access: {e}")
        return False

if __name__ == "__main__":
    print("Setting up R2 bucket for public access...")
    success = setup_r2_public_access()
    
    if success:
        print("\n🎉 R2 bucket is now configured for public access!")
        print("You can now access files via the public URL.")
    else:
        print("\n❌ Failed to setup public access.")
        print("Please check your R2 settings in Cloudflare Dashboard.")
