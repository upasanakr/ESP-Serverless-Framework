import os
import boto3
import io
import struct

# S3 client to interact with S3 buckets
s3 = boto3.client('s3')

def resize_image(image_data, new_width, new_height):
    old_width, old_height = struct.unpack('>II', image_data[:8])
    image_data = image_data[8:]

    aspect_ratio = old_width / old_height
    new_ratio = new_width / new_height

    if aspect_ratio > new_ratio:
        new_height = int(new_width / aspect_ratio)
    else:
        new_width = int(new_height * aspect_ratio)

    resized_data = struct.pack('>II', new_width, new_height) + image_data

    return resized_data

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Check if the object is an image (you can modify this check based on your naming convention)
        if not key.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            continue

        # Define the resize parameters
        new_width = 400  # Set your desired width
        new_height = 400  # Set your desired height

        # Read the image from the source S3 bucket
        response = s3.get_object(Bucket=bucket, Key=key)
        image_content = response['Body'].read()

        # Resize the image
        resized_image_data = resize_image(image_content, new_width, new_height)

        # Upload the resized image to a target S3 bucket
        target_bucket = 'image.resize.folder'
        target_key = f'resized/{os.path.basename(key)}'
        s3.put_object(Bucket=target_bucket, Key=target_key, Body=resized_image_data)
