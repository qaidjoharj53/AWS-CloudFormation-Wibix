import boto3
import argparse
from botocore.exceptions import ClientError

def get_stack_resources(stack_name):
    # Fetch all resources associated with a CloudFormation stack
    cf_client = boto3.client('cloudformation')
    try:
        response = cf_client.describe_stack_resources(StackName=stack_name)
        return response.get('StackResources', [])
    except ClientError as e:
        print(f"Error fetching stack resources: {e}")
        return []

def get_ec2_instances():
    # Fetch all EC2 instances in the region
    ec2_client = boto3.client('ec2')
    try:
        response = ec2_client.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'InstanceId': instance['InstanceId'],
                    'InstanceType': instance['InstanceType'],
                    'State': instance['State']['Name'],
                    'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                    'PublicIpAddress': instance.get('PublicIpAddress', 'N/A')
                })
        return instances
    except ClientError as e:
        print(f"Error fetching EC2 instances: {e}")
        return []

def get_s3_buckets():
    # Fetch all S3 buckets
    s3_client = boto3.client('s3')
    try:
        response = s3_client.list_buckets()
        buckets = []
        for bucket in response['Buckets']:
            location = s3_client.get_bucket_location(Bucket=bucket['Name'])
            buckets.append({
                'Name': bucket['Name'],
                'CreationDate': bucket['CreationDate'].strftime('%Y-%m-%d'),
                'Region': location.get('LocationConstraint', 'us-east-1')
            })
        return buckets
    except ClientError as e:
        print(f"Error fetching S3 buckets: {e}")
        return []

def generate_inventory_report(stack_name):
    # Generate an inventory report for the AWS account
    print(f"\nGenerating inventory report for stack: {stack_name}\n")
    
    # Get stack resources
    stack_resources = get_stack_resources(stack_name)
    print(f"Stack Resources ({len(stack_resources)}):")
    for resource in stack_resources:
        print(f"  - {resource['ResourceType']}: {resource['PhysicalResourceId']}")
    
    # Get EC2 instances
    ec2_instances = get_ec2_instances()
    print(f"\nEC2 Instances ({len(ec2_instances)}):")
    for instance in ec2_instances:
        print(f"  - {instance['InstanceId']} ({instance['InstanceType']}): {instance['State']}")
    
    # Get S3 buckets
    s3_buckets = get_s3_buckets()
    print(f"\nS3 Buckets ({len(s3_buckets)}):")
    for bucket in s3_buckets:
        print(f"  - {bucket['Name']} (Created: {bucket['CreationDate']}, Region: {bucket['Region']})")

def main():
    parser = argparse.ArgumentParser(description='AWS Inventory Script')
    parser.add_argument('--stack-arn', required=True, help='CloudFormation Stack ARN or Name')
    args = parser.parse_args()
    
    # Generate the inventory report
    generate_inventory_report(args.stack_arn)

if __name__ == '__main__':
    main()