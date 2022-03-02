from curses import keyname
from sqlalchemy import create_engine
import yaml
import boto3
import pandas as pd 
from typing import Optional

class RacingPostUploader():
    """
    Class for uploading tabular data, JSON data and images into AWS S3 and RDS
    """
    def __init__(self):
        aws_config = self.read_cloud_config()
        postgre_config = aws_config['aws-postgresql']

        db_type = postgre_config["dbtype"]
        db_api = postgre_config["dbapi"]
        user = postgre_config["username"]
        password = postgre_config["password"]
        endpoint = postgre_config["endpoint"]
        port = postgre_config["port"]
        database = postgre_config["database"]

        print(f"Create postgreSQL engine {db_type}+{db_api}://{user}:*******@{endpoint}:{port}/{database}")
        self.engine = create_engine(f"{db_type}+{db_api}://{user}:{password}@{endpoint}:{port}/{database}")
        self.engine.connect()

        self.s3_bucket = aws_config["aws-s3"]["bucket"]
        
    @staticmethod
    def read_cloud_config(config_file : str = "./aws.yaml") -> dict:
        """
        Helper function to read S3 and RDS config

        Parameters
        =================
        config_file: str
            File path for the config file

        Returns 
        =================
        dict:
            AWS config in dictionary format

        """
        # read config
        with open(config_file, "r") as f:
            aws_config = yaml.safe_load(f)

        return aws_config

    def upload_postgreSQL(self, dataframe : pd.DataFrame, table_name : str, if_existed : str = "append") -> None:
        """
        Upload dataframe into RDS (PostgreSQL)

        Parameters
        =================
        dataframe: pd.DataFrame
            Dataframe that represening data in tabular format
        table_name: str
            Table's name in RDS
        if_exists: str
            Use "append" to append to the table or use "replace" to replace the entire table

        """
        dataframe.to_sql(table_name, self.engine, if_exists=if_existed)

    def get_postgreSQL(self, table_name : str) -> Optional[pd.DataFrame]:
        """
        Read dataframe from RDS (PostgreSQL)

        Parameters
        =================
        table_name: str
            Table's name in RDS

        Returns
        =================
        Optional[pd.DataFrame]:
            Dataframe retrived from RDS or None if table not found

        """

        try:
            return pd.read_sql_table(table_name, self.engine)
        except ValueError:
            pass    
            
        return None

    def upload_to_s3(self, file_path : str, key_name : str, busket : str = None) -> str:
        """
        Upload file into S3

        Parameters
        =================
        file_path: str
            File's path of the uploading file
        key_name: str
            Key name for file in S3. To saved the file with directory, 
            use {folder}/{filename} as keyname
        busket: str
            The busket to store the file
            Default: None, it means it will read the busket name from the config file
            
        Returns
        =================
        str:
            URL for the uploaded file in S3
        """

        if not busket:
            busket = self.s3_bucket

        s3_client = boto3.client('s3')
        response = s3_client.upload_file(file_path, busket, key_name)

        bucket_location = boto3.client('s3').get_bucket_location(Bucket=busket)

        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            bucket_location['LocationConstraint'],
            busket,
            key_name)

        return object_url

    def download_from_s3(self, file_path : str, key_name : str, busket : str = None) -> None:
        """
        Download file from S3

        Parameters
        =================
        file_path: str
            File's path you want to save the file
        key_name: str
            Key name for file in S3. To matched the file with directory, 
            use {folder}/{filename} as keyname
        busket: str
            The busket to store the file
            Default: None, it means it will read the busket name from the config file
        """

        if not busket:
            busket = self.s3_bucket

        s3_client = boto3.client('s3')
        s3_client.download_file(busket, file_path, key_name)

    def close_connection(self) -> None:
        """
        Close any opened DB connection
        """
        self.engine.dispose()