"""Quick start script for GarutVON FastAPI server.

Run this to start the FastAPI server on http://127.0.0.1:8000
Then connect the dev client to http://127.0.0.1:8000/api
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv(".env")
load_dotenv(".env.local", override=True)
load_dotenv("local.env", override=True)

if __name__ == "__main__":
    import uvicorn
    from garutvon.api_prod.main import create_app
    
    app = create_app()
    
    print("""
    ╔════════════════════════════════════════════╗
    ║     GarutVON FastAPI Server Starting      ║
    ╠════════════════════════════════════════════╣
    ║  Server:  http://127.0.0.1:8000           ║
    ║  API:     http://127.0.0.1:8000/api       ║
    ║  Docs:    http://127.0.0.1:8000/docs      ║
    ║                                            ║
    ║  Dev Client URL: http://127.0.0.1:8000/api║
    ╚════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
