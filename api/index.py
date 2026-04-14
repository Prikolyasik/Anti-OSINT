import json


def _wsgi_handler(environ, start_response):
    status = '200 OK'
    headers = [
        ('Content-Type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', '*'),
    ]
    start_response(status, headers)
    response = {
        "status": "ok",
        "message": "Python serverless работает!",
        "path": environ.get('PATH_INFO', ''),
    }
    return [json.dumps(response, ensure_ascii=False).encode('utf-8')]


app = _wsgi_handler
application = _wsgi_handler
handler = _wsgi_handler
