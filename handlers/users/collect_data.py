from utils import send_req


async def collect_me_data(token, field_name=None):
    response = await send_req.application_forms_me(token)

    if response.get('status_code') == 404:
        return False

    if field_name is None:
        return response

    try:
        value = response[field_name]
        if value is not None:
            return value
        if field_name == 'src':
            return response['user_education']['src']
    except KeyError:
        return False

    return None
