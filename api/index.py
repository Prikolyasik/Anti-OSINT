def handler(environ, start_response):
    """Минимальный WSGI handler для теста."""
    import json
    
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
