import os
import logging
import requests
from data.config import domain_name, origin

logger = logging.getLogger(__name__)


def upload_file(token: str, filename: str, usage: str = 'diploma') -> requests.Response:
    url = f"https://{domain_name}/v1/files/upload"
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Origin': origin,
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
    full_path = os.path.join(project_dir, filename)

    try:
        with open(full_path, 'rb') as f:
            files = {
                'file': (os.path.basename(full_path), f, 'image/jpeg'),
                'associated_with': (None, 'users'),
                'usage': (None, usage),
            }
            response = requests.post(url, headers=headers, files=files)
        return response
    except FileNotFoundError:
        logger.error("File not found: %s", full_path)
        raise


# Backward compatibility aliases
def upload_new_file(token, filename):
    return upload_file(token, filename, 'diploma')

def upload_new_file_sertificate(token, filename):
    return upload_file(token, filename, 'certificate')

def upload_new_file_transcript(token, filename):
    return upload_file(token, filename, 'transcript')

def work_experince_file_upload(token, filename):
    return upload_file(token, filename, 'work_experience')
