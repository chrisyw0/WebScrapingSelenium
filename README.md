# Racing Post Web Scraping using Selenium

## Description
This project aims at capturing race results from Racing post fast result and result detail page. You can input the url of a specific date to get all results for that date.

For example, the following URL will get results for today's races
- https://www.racingpost.com/fast-results/

While this URL will get results of races in 22nd Feb 2022 
- https://www.racingpost.com/results/2022-02-22/time-order/

The scraper will capture almost every thing in the detail page for every race listed in the fast result page. The captured data will be saved into a json file. In addition, it will download the silk for each horse in the races and save them into a folder. You can configure the URL, image folder and raw data (json) folder path and file name by inputting arguments when you run the scraper. The script will create folders if needed. 

## Run
> python racing_post_scraper.py *URL* *raw data file* *image folder*

### Parameters

**URL: str (Optional)**
    URL for the fast result page you want to capture the result. Default: https://www.racingpost.com/fast-results/

**Image folder: str (Optional)**
    Folder path for saving the image (racing silks). Imtermidate folders will be created if needed Default: ./images

**Raw data file: str (Optional)**
    Folder path for saving the image (racing silks). Imtermidate folders will be created if needed Default: ./raw_data/*%Y%m%d*.json (Today Date in %Y%m%d format, e.g. ./raw_data/20220222.json)

## Result

**Raw data file: json**
    Please see the sample json file in raw_data folder in this repository 

**Images:**
    Expect a 2-layer folder storing the images, e.g. ./images/*UUID*/*file name.svg*
    where each UUID will be matched to the UUID field of each race, and actual image name will be matched to the horse_silk field in the raw data file.

## Require package
- python
- selenium
- webdriver-manager

## TODO: 
- Docker configuration
- Cloud storage and DB configuration
- Unit test
- ...