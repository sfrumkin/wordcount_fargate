import json
import base64
from string import punctuation, whitespace
import re
import boto3
import botocore.exceptions
from botocore.exceptions import NoCredentialsError
import uuid
import os
from botocore.client import Config

tmpFile = "/tmp/results.json"
REGION = os.environ['REGION']


def upload_to_aws(local_file, s3_file):
    s3 = boto3.client('s3', endpoint_url=f'https://s3.{REGION}.amazonaws.com', config=Config(s3={'addressing_style': 'virtual'}))

    s3.upload_file(local_file, os.environ['BUCKET_NAME'], s3_file)

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': os.environ['BUCKET_NAME'],
            'Key': s3_file
        },
        ExpiresIn=24 * 3600
    )

    return url


def generate_words_counter(texts):
    words_counter = {}

    for word in re.split(f'[{punctuation}{whitespace}]', texts):
        word_lower_case = word.strip(punctuation).lower()

        if len(word_lower_case) == 0:
            continue

        if word_lower_case not in words_counter:
            words_counter[word_lower_case] = 0

        words_counter[word_lower_case] += 1
    
    return words_counter


def save_word_counter(word_counter, file_name):
    word_counter_json = json.dumps(word_counter, indent=4)

    with open(file_name, "w") as outfile:
        outfile.write(word_counter_json)


def request_handler(event):
    file_upload = base64.b64decode(event["body"])
    return file_upload.decode('utf-8')


def successful_response(url):
    return create_answer(200, json.dumps({'url': url}))


def create_answer(status_code, message):
    return {
        "statusCode": status_code,
        "body": message
    }


def lambda_handler(event, context):

    try:
        texts = request_handler(event)

        words_counter = generate_words_counter(texts)

        save_word_counter(words_counter, tmpFile)

        url = upload_to_aws(tmpFile, f'{str(uuid.uuid4())}.txt')

        return successful_response(url)

    except FileNotFoundError:
        return create_answer(404, "File Not Found")
    except NoCredentialsError:
        return create_answer(401, "No Credentials")
    except Exception as e:
        return create_answer(400, str(e))

