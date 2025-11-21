from os import environ

from dotenv import load_dotenv


load_dotenv()

DB_HOST = environ['DB_HOST']
DB_NAME = environ['DB_NAME']
DB_USER = environ['DB_USER']
DB_PASSWORD = environ['DB_PASSWORD']

JWT_REFRESH_LIFETIME_DAYS = int(environ['JWT_REFRESH_LIFETIME_DAYS'])
JWT_ACCESS_LIFETIME_MINUTES = int(environ['JWT_ACCESS_LIFETIME_MINUTES'])
