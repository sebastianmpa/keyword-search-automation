from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import logging

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger("mysql_connection")

class Settings(BaseSettings):
    # MySQL
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE")

settings = Settings()

def get_mysql_config():
    return {
        "host": settings.MYSQL_HOST,
        "user": settings.MYSQL_USER,
        "password": settings.MYSQL_PASSWORD,
        "database": settings.MYSQL_DATABASE,
    }

def get_mysql_connection():
    """
    Crea y retorna una conexión a MySQL usando la configuración de settings.
    
    Returns:
        mysql.connector.connection: Conexión activa a MySQL
    """
    try:
        config = get_mysql_config()
        connection = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            autocommit=True
        )
        
        if connection.is_connected():
            logger.info(f"Conexión exitosa a MySQL: {config['host']}/{config['database']}")
            return connection
            
    except Error as e:
        logger.error(f"Error conectando a MySQL: {str(e)}")
        raise