def get_request(context):
    try:
        request = context.get('request')
    except KeyError:
        raise KeyError({
            'error': 'request was not received'
        })
    return request
