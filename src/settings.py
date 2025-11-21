from os import environ

from dotenv import load_dotenv


load_dotenv()

DB_HOST = environ['DB_HOST']
DB_NAME = environ['DB_NAME']
DB_USER = environ['DB_USER']
DB_PASSWORD = environ['DB_PASSWORD']
