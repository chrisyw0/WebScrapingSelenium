from curses import keyname
from sqlalchemy import create_engine
import yaml
import boto3
import pandas as pd 

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
    def read_cloud_config(config_file="./aws.yaml"):
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

    def upload_postgreSQL(self, dataframe, table_name):
        """
        Upload dataframe into RDS (PostgreSQL)

        Parameters
        =================
        dataframe: pd.DataFrame
            Dataframe that represening data in tabular format
        table_name: str
            Table's name in RDS

        """
        dataframe.to_sql(table_name, self.engine, if_exists='append')

    def get_postgreSQL(self, table_name):
        """
        Read dataframe from RDS (PostgreSQL)

        Parameters
        =================
        table_name: str
            Table's name in RDS

        Returns
        =================
        pd.DataFrame:
            Dataframe retrived from RDS
        """
        
        return pd.read_sql_table(table_name, self.engine)

    def upload_to_s3(self, file_path, key_name, busket=None):
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

    def download_from_s3(self, file_path, key_name, busket=None):
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

    def close_connection(self):
        """
        Close any opened DB connection
        """
        self.engine.dispose()