from dataclasses import dataclass
from unittest import result
from webscraper import WebScrapper
import sys
import pprint
import random
import time
import uuid
import json
import os
from datetime import datetime
import pandas as pd
from collections import defaultdict
from racing_post_uploader import RacingPostUploader
from dataclasses import dataclass, field, asdict

@dataclass
class RacingPostPrizeRecord():
    """
    Data Class for storing prize records for a race
    """
    rank: list = field(default_factory=list)
    prize: list = field(default_factory=list)

    def add_prize_rank(self, this_rank, this_prize):
        """
        A helper function for setting rank and prize

        Parameters
        ===============
        this_rank: str
            Rank (1st, 2nd, ...)
        prize: str
            Prize for the rank, it usually start with currency symbol ($/£/¢...) 
            and formatted with ","
            E.g. ($1,000.21)

        """
        self.rank.append(this_rank)
        self.prize.append(this_prize)

@dataclass
class RacingPostHorseRecord():
    """
    Data Class for storing horse records for a race
    """
    horse_rank: str = None,
    horse_draw: str = None,
    horse_length: str = None,

    horse_no: str =None,
    horse_name: str = None,
    horse_country: str = None,
    horse_odd: str = None,
    horse_silk_url: str = None,

    horse_jockey: str = None,
    horse_trainer: str = None,

    horse_age: str = None,
    horse_st: str = None,
    horse_extra_weight: str = None,
    horse_head_gear: str = None,
    horse_lb: str = None,

    horse_or: str = None,
    horse_ts: str = None,
    horse_rpr: str = None,
    horse_mr: str = None,

    horse_comment: str = None,
    horse_silk: str = None,

    @classmethod
    def from_dict(cls, dictionary):
        """
        Create this object from a dictionary

        Parameters
        ==============
        dictionary: dict
            Dictionary for storing all keys and values matching attributes of this data class

        """
        result = cls()

        for k, v in dictionary.items():
            setattr(result, k, v)

        return result

@dataclass
class RacingPostRaceRecord():
    """
    Data Class for storing race records
    """

    url: str = None
    time: str = None
    date: str = None
    title: str = None
    course: str = None
    race_class: str = None
    rating: str = None
    distance: str = None
    condition: str = None
    prize: RacingPostPrizeRecord = None
    horse_rank: list = field(default_factory=list)
    UUID: str = None
    race_info_comment: str = None
    race_extra_info: str = None

    @classmethod
    def from_dict(cls, dictionary):
        """
        Create this object from a dictionary

        Parameters
        ==============
        dictionary: dict
            Dictionary for storing all keys and values matching attributes of this data class

        """

        result = cls()
        for k, v in dictionary.items():
            if k == 'horse_rank' and type(v) == list:
                v = [RacingPostHorseRecord().from_dict(horse_dict) for horse_dict in v]

            elif k == 'prize' and type(v) == dict:
                record = RacingPostPrizeRecord()
                for subkey, subvalue in v.items():
                    record.add_prize_rank(subkey, subvalue)

                v = record
                
            setattr(result, k, v)

        return result

    def to_dictionary(self):
        """
        Convert this object to a dictionary

        Returns
        ==============
        dict
            Dictionary that storing all attributes of this data class

        """

        result_dict = asdict(self)
        result_dict['prize'] = { k: v for k, v in zip(self.prize.rank, self.prize.prize)}
        result_dict['horse_rank'] = [asdict(horse) for horse in self.horse_rank]

        return result_dict

class RacingPostFastResult(WebScrapper):
    """
    This is a class (inherent of WebScrapper) for capturing fast result for RacingPost.com
    """
    def process(self):
        """
        Process the web page with Selenium. The steps are as follows:
        1. Open URL in Chrome
        2. Skip advertisement (if needed)
        3. Accept cookies
        4. Process main page and detail page
        5. Close all the window
        6. Download images (Silk)
        7. Save data in JSON format
        8. Upload raw data (JSON) and images to AWS S3, and in table format in AWS RDS

        This is the entry point if you want the whole process.
        """

        self.races = None

        self.load_url()
        self.accept_cookies()

        time.sleep(10)
        self.skip_ads()

        self.process_main_page()
        self.stop_scraping()

        self.download_images()
        self.save_raw_data()

        print(f"Finishing scraping")
        print(f"============================")
        pprint.pprint(self.races)
        print(f"============================")
        
        self.uploader = RacingPostUploader()

        self.upload_s3()
        self.upload_rds()
        
        self.uploader.close_connection()

    def restore_cache_result(self):
        """
        Restore from json file
        """
        with open(self.out_path+self.out_file, "r") as f:
            race_list = json.load(f)
        
        self.races = [RacingPostRaceRecord.from_dict(race) for race in race_list]

    def load_url(self, wait_seconds=10, wait_until=None):
        """
        Load URL until the accept cookies button clickable
        """
        xpath_accept_cookies = "//*[@id=\"truste-consent-button\"]"

        until = self.get_EC_element_clickable(xpath=xpath_accept_cookies)
        super().load_url(wait_seconds, until)

    def skip_ads(self):
        """
        Ask Chrome to open the url and wait the accept cookies button appear
        """
        # skip ads
        self.click_button(xpath="//button[contains(@class, 'ab-close-button')]")

    def accept_cookies(self):
        """
        Accept cookies
        """
        # accept cookies
        self.click_button(xpath="//*[@id=\"truste-consent-button\"]")
        print("Accept cookies")
        
        time.sleep(2)

    def process_main_page(self):
        """
        Process the main page to get a list of detail page, and go into every valid detail page 
        """

        until = self.get_EC_element_presence(xpath="//div[contains(@class, 'rp-timeView__list')]")
        self.wait_until(until)

        self.move_to_element(xpath="//div[contains(@class, 'rp-timeView__list')]")

        # get a list of result item view
        timeView_list = self.get_web_element(xpath="//div[contains(@class, 'rp-timeView__list')]")
        elements = self.get_web_elements(parent=timeView_list, xpath="./div[contains(@class, 'rp-timeView__listItem') and not(contains(@class, 'rp-emptyResult'))]")

        races = []

        if elements:
            print(f"{len(elements)} races found")

            # for each result, click the full result button to go to detail view            
            for element in elements:
                success, full_result_button = self.click_button(parent=element, xpath=".//a[contains(text(), \"Full result\")]")

                if not success:
                    # imcompleted result, skip this record
                    continue

                race_info_dict = self.process_detail_page(full_result_button.get_attribute("href"))
                races.append(race_info_dict)

                # close and move to the window of the main page
                self.close_current_window()
                self.switch_to_new_window()

                # randomly sleep to avoid being suspicious 
                sleep_second = random.randrange(5.0, 10.0)
                time.sleep(sleep_second)

                #TODO: TESTING
                # break

        self.races = races

    def process_detail_page(self, url, move_to_new_window=True):
        """
        Process the detail page for all the information, 
        if the detail page is shown in a new window, it will wait until a new window opened

        Parameters
        ------------
        url: str
            The URL of the detail page
        
        move_to_new_window: bool
            Whether the detail page is appear in a new window

        Returns
        ------------
        RacingPostRaceRecord:
            Race record captured from the detail page

        """

        print(f"Prasing race detail for {url}")

        # wait until a new window popup
        if move_to_new_window:
            if self.get_number_of_windows() == 1:
                until = self.get_EC_window_open()
                self.wait_until(until)

            self.switch_to_new_window()

        until = self.get_EC_element_presence(xpath="//section[contains(@class, 'rp-resultsWrapper__section')]")
        self.wait_until(until)
        
        # race information (header labels)
        race_info = self.get_web_element(xpath="//div[contains(@class, 'rp-raceTimeCourseName')]")

        race_time = self.get_web_element(parent=race_info, xpath="./h1/span[contains(@class, 'rp-raceTimeCourseName__time')]")
        race_course = self.get_web_element(parent=race_info, xpath="./h1/a[contains(@class, 'rp-raceTimeCourseName__name')]")
        race_date = self.get_web_element(parent=race_info, xpath="./h1/span[contains(@class, 'rp-raceTimeCourseName__date')]")

        race_detail = self.get_web_element(parent=race_info, xpath="./div[contains(@class, 'rp-raceTimeCourseName__info')]")

        race_title = self.get_web_element(parent=race_detail, xpath="./h2[contains(@class, 'rp-raceTimeCourseName__title')]")

        race_detail_container = self.get_web_element(parent=race_detail, xpath="./span[contains(@class, 'rp-raceTimeCourseName__info_container')]")
        race_rating = self.get_web_element(parent=race_detail_container, xpath="./span[contains(@class, 'rp-raceTimeCourseName_ratingBandAndAgesAllowed')]")
        race_distance = self.get_web_element(parent=race_detail_container, xpath="./span[contains(@class, 'rp-raceTimeCourseName_distance')]")
        race_class = self.get_web_element(parent=race_detail_container, xpath="./span[contains(@class, 'rp-raceTimeCourseName_class')]")
        race_condition = self.get_web_element(parent=race_detail_container, xpath="./span[contains(@class, 'rp-raceTimeCourseName_condition')]")

        race_detail_div = self.get_web_element(parent=race_detail_container, xpath="./div[@data-test-selector='text-prizeMoney']")
        
        prize_list = race_detail_div.text.split()
        prize_info = RacingPostPrizeRecord()

        for i in range(int(len(prize_list)/2)):
            prize_info.add_prize_rank(prize_list[2*i], prize_list[2*i+1])

        race_info = RacingPostRaceRecord()
        race_info.url = url
        race_info.time = race_time.text if race_time else None
        race_info.date = race_date.text if race_date else None
        race_info.title = race_title.text if race_title else None
        race_info.course = race_course.text if race_course else None
        race_info.rating = race_rating.text if race_rating else None
        race_info.distance = race_distance.text if race_distance else None
        race_info.race_class = race_class.text if race_class else None
        race_info.condition = race_condition.text if race_condition else None
        race_info.prize = prize_info
        
        # horse table
        horse_table = self.get_web_element(xpath="//table[contains(@class, 'rp-horseTable__table')]")
        horse_row = self.get_web_elements(parent=horse_table, xpath="./tbody/tr")

        cache_record = None

        # iterate over rows to capture the information of each horse, 
        # each row may be either horse information, comment or separator, 
        # we process main and comment rows only
        for row in horse_row:
            row_class = row.get_attribute("class")

            # main row
            if "rp-horseTable__mainRow" in row_class:
                # if the main row appear again, it means it is showing information for another horse
                # put the cache record into a list
                if cache_record:
                    race_info.horse_rank.append(cache_record)
                
                cache_record = RacingPostHorseRecord()

                # the first td doesn't come with a class, capture the inner div directly
                horse_pos_div = self.get_web_element(parent=row, xpath="./td/div[contains(@class, 'rp-horseTable__pos')]")

                horse_pos = self.get_web_element(parent=horse_pos_div, xpath="./div/span[contains(@class, 'rp-horseTable__pos__number')]")
                horse_draw = self.get_web_element(parent=horse_pos_div, xpath="./div/span/sup[contains(@class, 'rp-horseTable__pos__draw')]")

                horse_length = self.get_web_element(parent=horse_pos_div, xpath="./div/span[contains(@class, 'rp-horseTable__pos__length')]")

                if horse_pos and horse_draw:
                    horse_pos_text = horse_pos.text.replace(horse_draw.text, "").strip()
                    horse_draw_text = horse_draw.text.replace("(", "").replace(")", "").strip()
                else:
                    horse_pos_text = horse_pos.text if horse_pos else None
                    horse_draw_text = horse_draw.text if horse_draw else None

                cache_record.horse_rank = horse_pos_text
                cache_record.horse_draw = horse_draw_text
                cache_record.horse_length = horse_length.text if horse_length else None
                # end of the left most td

                # we iterate over tds, they are either with class type horse, human, age, wgt,
                # or data ending with OR, TS, RPR or MR
                main_row_tds = self.get_web_elements(parent=row, xpath="./td")

                for td in main_row_tds:
                    td_class = td.get_attribute("class")

                    if 'rp-horseTable__horseCell' in td_class:
                        horse_cell_div = self.get_web_element(parent=td, xpath="./div[contains(@class, 'rp-horseTable__horseContainer')]")

                        horse_info = self.get_web_element(parent=horse_cell_div, xpath="./div[contains(@class, 'rp-horseTable__info')]")

                        horse_no = self.get_web_element(parent=horse_info, xpath="./span[contains(@class, 'rp-horseTable__saddleClothNo')]")
                        horse_name = self.get_web_element(parent=horse_info, xpath=".//a[contains(@class, 'rp-horseTable__horse__name')]")

                        horse_name_children = self.get_web_elements(parent=horse_name, xpath="./*")
                        horse_name_text = None

                        # get rid of child element containing unused title
                        if horse_name:
                            horse_name_text = horse_name.text

                            for child in horse_name_children:
                                horse_name_text = horse_name_text.replace(child.text, "")

                        horse_country = self.get_web_element(parent=horse_info, xpath=".//span[contains(@class, 'rp-horseTable__horse__country')]")
                        horse_odd = self.get_web_element(parent=horse_info, xpath=".//span[contains(@class, 'rp-horseTable__horse__price')]")

                        # for silk, capture the url only, will start downloading the images after capturing all races
                        horse_silk = self.get_web_element(parent=horse_cell_div, xpath=".//img[contains(@class, 'rp-horseTable__silk')]")

                        cache_record.horse_no = horse_no.text if horse_no else None
                        cache_record.horse_name = horse_name_text
                        cache_record.horse_country = horse_country.text if horse_country else None
                        cache_record.horse_odd = horse_odd.text if horse_odd else None
                        cache_record.horse_silk_url = horse_silk.get_attribute("src") if horse_silk else None
                        
                        horse_human = self.get_web_element(parent=horse_info, xpath="./div[contains(@class, 'rp-horseTable__human')]")
                        horse_human_wrapper = self.get_web_elements(parent=horse_human, xpath="./span[contains(@class, 'rp-horseTable__human__wrapper')]")
            
                        for wrapper in horse_human_wrapper:
                            prefix = wrapper.get_attribute("data-prefix")
                            if "J:" in prefix:
                                horse_jockey = self.get_web_element(parent=wrapper, xpath="./a[contains(@class, 'rp-horseTable__human__link')]")
                                cache_record.horse_jockey = horse_jockey.text if horse_jockey else None
                            elif "T:" in prefix:
                                horse_trainer = self.get_web_element(parent=wrapper, xpath="./a[contains(@class, 'rp-horseTable__human__link')]")
                                cache_record.horse_trainer = horse_trainer.text if horse_trainer else None

                    elif 'rp-horseTable__spanNarrow_age' in td_class:
                        horse_age = td
                        cache_record.horse_age = horse_age.text if horse_age else None
                    
                    elif 'rp-horseTable__wgt' in td_class:
                        horse_wgt_span = self.get_web_elements(parent=td, xpath="./span")
                
                        for span in horse_wgt_span:
                            span_class = span.get_attribute("class")

                            if 'rp-horseTable__st' in span_class:
                                horse_st = span
                                cache_record.horse_st = horse_st.text if horse_st else None
                            elif 'rp-horseTable__extraData' in span_class:
                                horse_extra_weight = self.get_web_element(parent=span, xpath="./span")
                                cache_record.horse_extra_weight = horse_extra_weight.text if horse_extra_weight else None
                            elif 'rp-horseTable__headGear' in span_class:
                                horse_head_gear = span
                                cache_record.horse_head_gear = horse_head_gear.text if horse_head_gear else None
                            elif span.get_attribute('data-test-selector') == 'horse-weight-lb':
                                horse_lb = span
                                cache_record.horse_lb = horse_lb.text if horse_lb else None

                    else:
                        data_ending = td.get_attribute("data-ending")

                        if data_ending and data_ending == "OR":
                            horse_or = td
                            cache_record.horse_or = horse_or.text if horse_or else None
                        elif data_ending and data_ending == "TS":
                            horse_ts = td
                            cache_record.horse_ts = horse_ts.text if horse_ts else None
                        elif data_ending and data_ending == "RPR":
                            horse_rpr = td
                            cache_record.horse_rpr = horse_rpr.text if horse_rpr else None
                        elif data_ending and data_ending == "MR":
                            horse_mr = td
                            cache_record.horse_mr = horse_mr.text if horse_mr else None

            # comment row    
            elif "rp-horseTable__commentRow" in row_class:
                horse_comment = self.get_web_element(parent=row, xpath='./td')
                cache_record.horse_comment = horse_comment.text if horse_comment else None

        if cache_record:
            race_info.horse_rank.append(cache_record)
        
        # additional race info
        race_info_ols = self.get_web_elements(xpath="//div[contains(@class, 'rp-raceInfo')]/ul/li")
        extra_infos = []

        # skip svg title for extra info
        for ol in race_info_ols:
            ol_text = ol.text
            ol_children = self.get_web_elements(parent=ol, xpath="./*/*")

            for child in ol_children:
                if child.tag_name == "svg":
                    svg_title = child.text
                    ol_text = ol_text.replace(svg_title, "")

            extra_infos.append(ol_text)
        
        race_info.race_extra_info = "\n".join(extra_infos)

        race_info_comment = self.get_web_element(xpath="//span[contains(@class, 'rp-raceInfo__comments')]")
        race_info.race_info_comment = race_info_comment.text if race_info_comment else None

        # assign the race with an UUID
        race_info.UUID = uuid.uuid5(uuid.NAMESPACE_URL, url).hex

        return race_info

    def save_raw_data(self):
        """
        Save raw data in json format. 
        It will create a folder if the folder specified in out_path doesn't exist.
        """
        os.makedirs(self.out_path, exist_ok=True)

        with open(self.out_path + self.out_file, 'w+') as file:
            json.dump([race.to_dictionary() for race in self.races], file, indent=4)

    def download_images(self):
        """
        Download images for each race and save it into image path
        """
        
        print("Downloading images...")
        for race in self.races:
            race_uuid = race.UUID
            for horse in race.horse_rank:
                horse_silk_url = horse.horse_silk_url

                if horse_silk_url:
                    this_image_path = self.image_path + race_uuid + "/" 

                    file_name = self.download_image(horse_silk_url, this_image_path)
                    horse.horse_silk = file_name

            sleep_second = random.randrange(3.0)
            time.sleep(sleep_second)

    def normalize_race_record(self, race_list=None):
        """
        Normalize the raw data into 3 tables (race information, prize information and horse records)
        Parameters
        ------------
        race_list: list[dict]
            A list for races in dictionary format
        """

        if not race_list:
            race_list = self.races

        race_info_dict = defaultdict(list)
        prize_info_dict = defaultdict(list)
        horse_info_dict = defaultdict(list)
       
        for race in race_list:
            race_dict = race.to_dictionary()
            race_id = race_dict["UUID"]
            
            for key, value in race_dict.items():
                if key == 'prize':
                    for prize_key, prize_value in value.items():
                        prize_info_dict["race_id"].append(race_id)
                        prize_info_dict["rank"].append(prize_key)
                        prize_info_dict["prize"].append(prize_value)

                elif key == 'horse_rank':
                    for horse in value:
                        horse_info_dict["race_id"].append(race_id)

                        for horse_key, horse_value in horse.items():
                            horse_info_dict[horse_key].append(horse_value)
                else:
                    race_info_dict[key].append(value)

        df_race_info = pd.DataFrame.from_dict(race_info_dict)
        df_prize_info = pd.DataFrame.from_dict(prize_info_dict)
        df_horse_info = pd.DataFrame.from_dict(horse_info_dict)

        return df_race_info, df_prize_info, df_horse_info

    def upload_s3(self):
        """
        Upload images and raw data file into s3. The key for raw data will be equal to raw_data/{input filename}
        and for images will be {UUID for each race}/{horse_silk}
        """

        # for testing only
        if not self.races:
            with open(self.out_path + self.out_file, "r") as f:
                self.races = json.load(f)

        # upload raw data into s3
        self.uploader.upload_to_s3(f"{self.out_path + self.out_file}", f"raw_data/{self.out_file}")

        # upload images into s3
        for race in self.races:
            race_id = race.UUID

            for horse in race.horse_rank:
                file_name = horse.horse_silk

                if file_name:
                    keyname = f"{race_id}/{file_name}"
                    self.uploader.upload_to_s3(f"{self.image_path}{keyname}", keyname)


    def upload_rds(self):
        """
        Upload raw data into tabular format into AWS RDS, it first normalize raw data into 3 tables
        (race_info, prize_info and horse_record) in pandas dataframe format, where prize info and 
        horse record has the foreign key "race_id" referencing to primary key "race_id" in race_info 
        table. 
        """
        
        if not self.races:
            with open(self.out_path + self.out_file, "r") as f:
                self.races = json.load(f)

        df_race, df_prize, df_horse = self.normalize_race_record()

        self.uploader.upload_postgreSQL(df_race, "race_info")
        self.uploader.upload_postgreSQL(df_prize, "prize_info")
        self.uploader.upload_postgreSQL(df_horse, "horse_record")

def main(url, out_path, out_file, image_path):
    """
    Main function of racing post scraper
    Parameters
    ----------
    url: str
        the url, it can be the URL for today result (https://www.racingpost.com/fast-results/) 
        or a specific date i.e. https://www.racingpost.com/results/2022-02-21/time-order/
    out_file: str
        the file path for the raw data file
    image_path: str
        the path that you want to save the image
    """

    print(f"Start scrapping for {url}")

    scraper = RacingPostFastResult(url, image_path, out_path, out_file)
    scraper.process()
    
if __name__ == "__main__":
    args = sys.argv[1:]
    
    today = datetime.now()

    url = args[0] if len(args) > 0 else "https://www.racingpost.com/fast-results/"
    out_file = args[1] if len(args) > 1 else f"./raw_data/{today.strftime('%Y%m%d')}.json"
    image_path = args[2] if len(args) > 2 else "./images/"

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("URL should start with http:// or https://")

    out_file_paths = out_file.split('/')

    out_filename = out_file_paths[-1]
    out_file_path = out_file[:-len(out_filename)]

    main(url, out_file_path, out_filename, image_path)