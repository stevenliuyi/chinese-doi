import requests
import time
import sys


def web_request(link, **kwargs):
    try:
        res = requests.get(link, timeout=10, **kwargs)
    except:
        # try once more after 5 seconds
        time.sleep(5)
        try:
            res = requests.get(link, timeout=20, **kwargs)
        except Exception as e:
            print(f'Connection to {link} failed: {e.__class__.__name__}')
            sys.exit(1)

    return res