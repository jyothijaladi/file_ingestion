import boto3
import json
from datetime import datetime
import logging
import re
import os

# set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s: %(asctime)s: %(message)s"
)
logger = logging.getLogger("data-ingestion-logger")
logger.setLevel(logging.INFO)


s3 = boto3.client("s3")
sns_client = boto3.client("sns")

# sns arn
topic_arn = os.environ["sns_topic"]


# exception class
class MyException(Exception):
    def __init__(self, message):
        self.message = message
        self.send_alert()

    def __str__(self):
        return self.message

    def send_alert(self):
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=self.message,
            Subject="Failed--movie-lens-data-ingestion-alert",
        )


# getting current datetime details
current_datetime = datetime.now()
day = current_datetime.day
year = current_datetime.year
month = current_datetime.month
hour = current_datetime.hour
minute = current_datetime.minute
second = current_datetime.second


def partition_logic(source_system, file, file_type, partition_string):
    file_path_string = ""
    if partition_string == "YEAR":
        file_path_string = f"{source_system}/{file}/year={year}/{file}_{year}_{month}_{day}.{file_type}"
    elif partition_string == "MONTH":
        file_path_string = f"{source_system}/{file}/year={year}/month={month}/{file}_{year}_{month}_{day}.{file_type}"
    elif partition_string == "DAY":
        file_path_string = f"{source_system}/{file}/year={year}/month={month}/day={day}/{file}_{year}_{month}_{day}.{file_type}"
    elif partition_string == "HOUR":
        file_path_string = f"{source_system}/{file}/year={year}/month={month}/day={day}/hour={hour}/{file}_{year}_{month}_{day}.{file_type}"
    elif partition_string == "MINUTE":
        file_path_string = f"{source_system}/{file}/year={year}/month={month}/day={day}/hour={hour}/minute={minute}/{file}_{year}_{month}_{day}.{file_type}"
    elif partition_string == "SECOND":
        file_path_string = f"{source_system}/{file}/year={year}/month={month}/day={day}/hour={hour}/minute={minute}/second={second}/{file}_{year}_{month}_{day}.{file_type}"

    return file_path_string


def handler(event, context):

    # loading configuration file
    logger.info(f"configuration file is loading")
    source_name = event["data_set"]
    # source_name = "movie-lens"
    bucket_name = "data-ing-code"
    response = s3.get_object(
        Bucket=bucket_name, Key=f"{source_name}/config/file_ingestion_config.json"
    )
    config_data = response["Body"].read().decode("utf-8")
    config = json.loads(config_data)
    logger.info(f"configuration file loaded successfully")

    source_system = config["source_system"]
    logger.info(f"the source system is {source_system}")
    successful_filepath_list = []

    try:

        data_pipeline_config = config["dataset_pipeline"]

        for data_asset_set in data_pipeline_config:
            raw_layer_config = data_asset_set["raw"]
            data_asset = data_asset_set["data_asset"]
            logger.info(f"processing data for data_asset {data_asset} to raw layer")

            source_bucket = raw_layer_config["source_bucket"]
            raw_bucket = raw_layer_config["raw_bucket"]
            file_pattern = raw_layer_config["file_pattern"]
            partition = raw_layer_config["partition"]
            file_type = raw_layer_config["file_type"]

            response = s3.list_objects_v2(Bucket=source_bucket)
            for obj in response.get("Contents", []):
                key = obj["Key"]
                filename = key.split("/")[1]
                if ".csv" in key:
                    copy_source = {"Bucket": source_bucket, "Key": key}
                    file = filename.split(".")[0]

                    if re.findall(f"^{file_pattern}", file):
                        file_path = partition_logic(
                            source_system, file, file_type, partition
                        )
                        s3.copy(
                            copy_source,
                            raw_bucket,
                            file_path,
                        )
                        successful_filepath_list.append(file_path)

    except Exception as e:
        logger.error("getting errors in processing files to raw layer")
        raise MyException(f"getting errors in processing files to raw layer {str(e)}")

    # sending success email
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message="All the files successfully loaded to raw layer",
        Subject="Success--movie-lens-data-ingestion-landing-raw",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"raw_file_paths": successful_filepath_list}),
    }
