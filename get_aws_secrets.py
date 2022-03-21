import os
import boto3
import base64
from botocore.exceptions import ClientError
import logging
import coloredlogs


def get_aws_secrets():
    logger = logging.getLogger(__name__)
    coloredlogs.install(logger=logger)

    env = os.environ.get("ENV")
    aws_region_name = os.environ.get("AWS_REGION_NAME")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY")
    aws_secret_access_key = os.environ.get("AWS_SECRET_KEY")
    aws_secret_name = os.environ.get("AWS_SECRET_NAME")

    env_file = f'.env.{env}' if env else '.env'

    client = boto3.client(
        service_name='secretsmanager',
        region_name=aws_region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=aws_secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException'\
                or e.response['Error']['Code'] == 'InternalServiceErrorException'\
                or e.response['Error']['Code'] == 'InvalidParameterException'\
                or e.response['Error']['Code'] == 'InvalidParameterException'\
                or e.response['Error']['Code'] == 'InvalidRequestException'\
                or e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.error(e.response['Error'])
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            if secret:
                with open(env_file, 'w+') as f:
                    f.write(secret)
                    f.close()
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            if decoded_binary_secret:
                with open(env_file, 'w+') as f:
                    f.write(decoded_binary_secret)
                    f.close()


if __name__ == '__main__':
    get_aws_secrets()
