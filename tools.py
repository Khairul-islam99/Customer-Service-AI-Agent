import os
import psycopg2
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Load environment variables from the .env file
load_dotenv()