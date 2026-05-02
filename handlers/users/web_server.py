from aiohttp import web
from data.config import port, university_site_url

async def handle(request):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Universitet haqida</title>
        <meta http-equiv="refresh" content="0; URL='{university_site_url}'" />
    </head>
    <body>
        <p>If you are not redirected automatically, follow this <a href='{university_site_url}'>link to the university site</a>.</p>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

app = web.Application()
app.router.add_get('/', handle)

def start_web_server():
    web.run_app(app, host='127.0.0.1', port=port, handle_signals=False)
