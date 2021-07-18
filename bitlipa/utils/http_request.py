import requests


def http_request(url, method='GET', **kwargs):
    try:
        response = requests.request(method=method, url=url, **kwargs)
        return response
    except requests.HTTPError as exc:
        return exc.request
