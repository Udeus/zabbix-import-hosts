def zabbix_url(url):
    if not url.endswith('/api_jsonrpc.php'):
        if not url.endswith('/'):
            url += '/'
        url += 'api_jsonrpc.php'
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    return url
