from fastapi import FastAPI

app = FastAPI(title='GarutVON API (minimal)', version='0.0.1')


@app.get('/health')
def health():
    return {'status': 'healthy', 'service': 'GarutVON API'}


@app.get('/version')
def version():
    return {'latest_version': '1.0.0'}
