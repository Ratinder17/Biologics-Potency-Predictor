# config.py
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from pymongo import MongoClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URIII")
    MONGO_DB_NAME = os.getenv("MONGO_DB")

    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    AZURE_ADI_ENDPOINT = os.getenv("AZURE_ADI_ENDPOINT")
    AZURE_ADI_KEY = os.getenv("AZURE_ADI_KEY")

    DEBUG_PRINT = True
    PRINT_EVERY_N = 60


mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client[Config.MONGO_DB_NAME]

openai_client = AzureOpenAI(
    api_version=Config.AZURE_OPENAI_API_VERSION,
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    api_key=Config.AZURE_OPENAI_KEY,
)


azure_di_client = DocumentAnalysisClient(
    endpoint=Config.AZURE_ADI_ENDPOINT,
    credential=AzureKeyCredential(Config.AZURE_ADI_KEY),
)