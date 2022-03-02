# Racing Post Web Scraping using Selenium

## Description
This project aims at capturing race results from Racing post fast result and result detail page. You can input the url of a specific date to get all results for that date.

For example, the following URL will get results for today's races
- https://www.racingpost.com/fast-results/

While this URL will get results of races in 22nd Feb 2022 
- https://www.racingpost.com/results/2022-02-22/time-order/

The scraper will capture almost every thing in the detail page for every race listed in the fast result page. The captured data will be saved into a json file. In addition, it will download the silk for each horse in the races and save them into a folder. You can configure the URL, image folder and raw data (json) folder path and file name by inputting arguments when you run the scraper. The script will create folders if needed. 

## Run
> python main.py *URL* *raw data file* *image folder* *force_capture*

### Parameters

**URL: str (Optional)**
URL for the fast result page you want to capture the result. 

Default: https://www.racingpost.com/fast-results/

**Image folder: str (Optional)**
Folder path for saving the image (racing silks). Imtermidate folders will be created if needed 

Default: ./images

**Raw data file: str (Optional)**
Folder path for saving the raw data (in json format). Imtermidate folders will be created if needed 

Default: ./raw_data/*%Y%m%d*.json (Today Date in %Y%m%d format, e.g. ./raw_data/20220222.json)

**Force Capture**
This option allow re-capturing the races that have been saved into DB previously. The existing records will be replaced by the newly captured records and uploaded in AWS RDS. Input *True* to enable this feature. 

Default False

## Result

**Raw data file: json**
Please see the sample json file in raw_data folder in this repository 

**Images:**
Expect a 2-layer folder storing the images, e.g. ./images/*UUID*/*file name.svg*
where each UUID will be matched to the UUID field of each race, and actual image name will be matched to the horse_silk field in the raw data file. To save loading, it will only store the winner horse's silk. 

## S3 and RDS integration
Besides saving the raw data and images locally, the script also uploads the files into AWS S3 and RDS. For S3, it simpliy stores the raws data and image files. For RDS, the raw data is firstly normalized into 3 tables (race, prize and horse), and then uploaded into PostgresSQL based DB. 

The yaml file stored the AWS connection related config, there is a sample file called *aws_config_sample.yaml* is included in this project. To change to configuration for uploading into your server, replace the content of your server and rename it as *aws.yaml*. 

## Testing
11 unit tests and 2 integration tests have been implemented using Pytest. For unit tests, it tests the whole process in each public function (mainly the steps of the whole process). For integration tests, one for checking data correctness of a race on a specific date. Another one for checking data format for yesterday's races. Please check /test/racing_post_test.py for details. 

## Require package
- python
- selenium
- webdriver-manager
- pytest
- awscli
- boto3
- psycopg2
- sqlalchemy
- pandas

## TODO: 
- Docker configuration
- ...