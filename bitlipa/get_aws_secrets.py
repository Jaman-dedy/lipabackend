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
    region_name = os.environ.get("REGION_NAME")
    secret_name = os.environ.get("SECRET_NAME")

    env_file = f'.env.{env}' if env else '.env'

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
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
