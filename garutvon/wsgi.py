import os

# Load environment variables before importing the app
from dotenv import load_dotenv

# Load from .env, .env.local, local.env in order
for env_file in [".env", ".env.local", "local.env"]:
    if os.path.exists(env_file):
        load_dotenv(env_file, override=False)

from garutvon import app

