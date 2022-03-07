from __future__ import annotations
from dataclasses import dataclass
from scrapers.webscraper import WebScrapper
import pprint
import random
import time
import uuid
import json
import os
import shutil
import pandas as pd
from collections import defaultdict
from racing_post.racing_post_uploader import RacingPostUploader
from dataclasses import dataclass, field, asdict
from typing import Any, Tuple, Optional

class Constant():
    XPATH_COOKIES = "//*[@id=\"truste-consent-button\"]"
    XPATH_AD_BUTTON = "//button[contains(@class, 'ab-close-button')]"
    XPATH_TIME_LIST = "//div[contains(@class, 'rp-timeView__list')]"
    XPATH_TIME_ITEM = "./div[contains(@class, 'rp-timeView__listItem') and not(contains(@class, 'rp-emptyResult'))]"
    XPATH_FULL_RESULT = ".//a[contains(text(), \"Full result\")]"
    XPATH_RESULT_SECTION = "//section[contains(@class, 'rp-resultsWrapper__section')]"
    XPATH_RESULT_RACE_INFO = "//div[contains(@class, 'rp-raceTimeCourseName')]"

    XPATH_RESULT_RACE_TIME = "./h1/span[contains(@class, 'rp-raceTimeCourseName__time')]"
    XPATH_RESULT_RACE_COURSE = "./h1/a[contains(@class, 'rp-raceTimeCourseName__name')]"
    XPATH_RESULT_RACE_DATE = "./h1/span[contains(@class, 'rp-raceTimeCourseName__date')]"

    XPATH_RESULT_RACE_DETAIL = "./div[contains(@class, 'rp-raceTimeCourseName__info')]"

    XPATH_RESULT_RACE_TITLE = "./h2[contains(@class, 'rp-raceTimeCourseName__title')]"

    XPATH_RESULT_RACE_DETAIL_CONTAINER = "./span[contains(@class, 'rp-raceTimeCourseName__info_container')]"
    XPATH_RESULT_RACE_RATING = "./span[contains(@class, 'rp-raceTimeCourseName_ratingBandAndAgesAllowed')]"
    XPATH_RESULT_RACE_DISTANCE = "./span[contains(@class, 'rp-raceTimeCourseName_distance')]"
    XPATH_RESULT_RACE_CLASS = "./span[contains(@class, 'rp-raceTimeCourseName_class')]"
    XPATH_RESULT_RACE_CONDITION = "./span[contains(@class, 'rp-raceTimeCourseName_condition')]"

    XPATH_RESULT_RACE_DETAIL_DIV = "./div[@data-test-selector='text-prizeMoney']"

    XPATH_RESULT_HORSE_TABLE = "//table[contains(@class, 'rp-horseTable__table')]"
    XPATH_RESULT_HORSE_ROW = "./tbody/tr"

    XPATH_RESULT_HORSE_POS_DIV = "./td/div[contains(@class, 'rp-horseTable__pos')]"

    XPATH_RESULT_HORSE_POS = "./div/span[contains(@class, 'rp-horseTable__pos__number')]"
    XPATH_RESULT_HORSE_DRAW = "./div/span/sup[contains(@class, 'rp-horseTable__pos__draw')]"

    XPATH_RESULT_HORSE_LENGTH = "./div/span[contains(@class, 'rp-horseTable__pos__length')]"

    XPATH_RESULT_HORSE_CELL_DIV = "./div[contains(@class, 'rp-horseTable__horseContainer')]"

    XPATH_RESULT_HORSE_INFO = "./div[contains(@class, 'rp-horseTable__info')]"

    XPATH_RESULT_HORSE_NO = "./span[contains(@class, 'rp-horseTable__saddleClothNo')]"
    XPATH_RESULT_HORSE_NAME = ".//a[contains(@class, 'rp-horseTable__horse__name')]"

    XPATH_RESULT_HORSE_COUNTRY = ".//span[contains(@class, 'rp-horseTable__horse__country')]"
    XPATH_RESULT_HORSE_ODD = ".//span[contains(@class, 'rp-horseTable__horse__price')]"

    XPATH_RESULT_HORSE_SILK = ".//img[contains(@class, 'rp-horseTable__silk')]"

    XPATH_RESULT_HORSE_HUMAN = "./div[contains(@class, 'rp-horseTable__human')]"
    XPATH_RESULT_HORSE_HUMAN_WRAPPER = "./span[contains(@class, 'rp-horseTable__human__wrapper')]"
    
    XPATH_RESULT_HORSE_JOCKEY = "./a[contains(@class, 'rp-horseTable__human__link')]"
    XPATH_RESULT_HORSE_JOCKEY_PREFIX = "J:"
    XPATH_RESULT_HORSE_TRAINER = "./a[contains(@class, 'rp-horseTable__human__link')]"
    XPATH_RESULT_HORSE_TRAINER_PREFIX = "T:"

    XPATH_RESULT_HORSE_WGT_SPAN = "./span"

    XPATH_RESULT_HORSE_TABLE_MAIN_ROW = "rp-horseTable__mainRow"
    XPATH_RESULT_HORSE_TABLE_COMMENT_ROW = "rp-horseTable__commentRow"
    
    XPATH_RESULT_MAIN_ROW_TDS = "./td"
    XPATH_RESULT_HORSE_TABLE_TD_HORSE_CELL = "rp-horseTable__horseCell"
    
    XPATH_RESULT_HORSE_TABLE_TD_AGE_CELL = 'rp-horseTable__spanNarrow_age'
    XPATH_RESULT_HORSE_TABLE_TD_WGT_CELL = 'rp-horseTable__wgt'

    XPATH_RESULT_HORSE_TABLE_ST = 'rp-horseTable__st'
    XPATH_RESULT_HORSE_TABLE_HEAD_GEAR = 'rp-horseTable__headGear'
    XPATH_RESULT_HORSE_TABLE_EXTRA_DATA = 'rp-horseTable__extraData'

    XPATH_RESULT_HORSE_EXTRA_WEIGHT = "./span"
    XPATH_RESULT_HORSE_COMMENT = "./td"

    XPATH_RESULT_RACE_INFO_OLS = "//div[contains(@class, 'rp-raceInfo')]/ul/li"
    XPATH_RESULT_RACE_INFO_COMMENT = "//span[contains(@class, 'rp-raceInfo__comments')]"

    XPATH_RESULT_OL_CHILDREN = "./*/*"
    XPATH_RESULT_HORSE_NAME_CHILDREN = "./*"

    ATTRIBUTE_CLASS = "class"
    ATTRIBUTE_DATA_ENDING = "data-ending"
    ATTRIBUTE_DATA_PREFIX = "data-prefix"
    ATTRIBUTE_DATA_TEST_SELECTOR = 'data-test-selector'
    ATTRIBUTE_DATA_ENDING_OR = "OR"
    ATTRIBUTE_DATA_ENDING_TS = "TS"
    ATTRIBUTE_DATA_ENDING_RPR = "RPR"
    ATTRIBUTE_DATA_ENDING_MR = "MR"

    ATTRIBUTE_TAG_SVG = "svg"

    ATTRIBUTE_DATA_HORSE_WEIGHT_LB = 'horse-weight-lb'

    RDS_TABLE_RACE_INFO = "race_info"
    RDS_TABLE_PRIZE_INFO = "prize_info"
    RDS_TABLE_HORSE_RECORD = "horse_record"

    RDS_TABLE_RACE_INFO_TEST = "race_info_test"
    RDS_TABLE_PRIZE_INFO_TEST = "prize_info_test"
    RDS_TABLE_HORSE_RECORD_TEST = "horse_record_test"

    def get_rds_tables_key(table_name, is_testing=False) -> Optional[str]:
        if table_name == Constant.RDS_TABLE_RACE_INFO:
            return Constant.RDS_TABLE_RACE_INFO_TEST if is_testing else Constant.RDS_TABLE_RACE_INFO
        elif table_name == Constant.RDS_TABLE_PRIZE_INFO:
            return Constant.RDS_TABLE_PRIZE_INFO_TEST if is_testing else Constant.RDS_TABLE_PRIZE_INFO
        elif table_name == Constant.RDS_TABLE_HORSE_RECORD:
            return Constant.RDS_TABLE_HORSE_RECORD_TEST if is_testing else Constant.RDS_TABLE_HORSE_RECORD

        return None

@dataclass
class RacingPostPrizeRecord():
    """
    Data Class for storing prize records for a race
    """
    rank: list = field(default_factory=list)
    prize: list = field(default_factory=list)

    def add_prize_rank(self, this_rank : str, this_prize : str) -> None:
        """
        A helper function for setting rank and prize

        Parameters
        --------------
        this_rank: str
            Rank (1st, 2nd, ...)
        prize: str
            Prize for the rank, it usually start with currency symbol ($/£/¢...) 
            and formatted with ","
            E.g. ($1,000.21)

        """
        self.rank.append(this_rank)
        self.prize.append(this_prize)

    def __eq__(self, other : Any) -> bool:
        if isinstance(other, self.__class__):
            if len(self.prize) != len(other.rank) or len(self.rank) != len(other.rank) \
                or len(other.prize) != len(other.rank):
                return False

            for i in range(len(other.rank)):
                if other.rank[i] != self.rank[i] or other.prize[i] != self.prize[i]:
                    return False
            
            return True
        else:
            return False

@dataclass
class RacingPostHorseRecord():
    """
    Data Class for storing horse records for a race
    """
    horse_rank: str = None
    horse_draw: str = None
    horse_length: str = None

    horse_no: str =None
    horse_name: str = None
    horse_country: str = None
    horse_odd: str = None
    horse_silk_url: str = None

    horse_jockey: str = None
    horse_trainer: str = None

    horse_age: str = None
    horse_st: str = None
    horse_extra_weight: str = None
    horse_head_gear: str = None
    horse_lb: str = None

    horse_or: str = None
    horse_ts: str = None
    horse_rpr: str = None
    horse_mr: str = None

    horse_comment: str = None
    horse_silk: str = None
    horse_silk_url_s3: str = None

    @classmethod
    def from_dict(cls: type[RacingPostHorseRecord], dictionary : dict) -> RacingPostHorseRecord:
        """
        Create this object from a dictionary

        Parameters
        --------------
        dictionary: dict
            Dictionary for storing all keys and values matching attributes of this data class

        """
        result = cls()

        for k, v in dictionary.items():
            setattr(result, k, v)

        return result

    def __eq__(self, other : Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

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
    race_id: str = None
    race_info_comment: str = None
    race_extra_info: str = None

    def __eq__(self, other : Any) -> bool:
        if isinstance(other, self.__class__):
            for key, value in self.__dict__.items():
                if key not in other.__dict__ or value != other.__dict__[key]:
                    return False
            
            return True
        else:
            return False

    @classmethod
    def from_dict(cls : type[RacingPostRaceRecord], dictionary : dict) -> RacingPostRaceRecord:
        """
        Create this object from a dictionary

        Parameters
        --------------
        dictionary: dict
            Dictionary for storing all keys and values matching attributes of this data class

        Returns
        --------------
        Self:
            An instance with attributes filled with the input dictionary

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

    def to_dictionary(self) -> dict:
        """
        Convert this object to a dictionary

        Returns
        -----------
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

    def __init__(self, url: str, image_path: str = None, out_path: str = None, out_file: str = None, force_capture: bool = False, is_testing : bool = False) -> None:
        super().__init__(url, image_path, out_path, out_file, force_capture, is_testing)
        self.uploader = RacingPostUploader()

        self.df_race_info = self.uploader.get_postgreSQL(\
            Constant.get_rds_tables_key(Constant.RDS_TABLE_RACE_INFO, self.is_testing))
        self.df_prize_info = self.uploader.get_postgreSQL(\
            Constant.get_rds_tables_key(Constant.RDS_TABLE_PRIZE_INFO, self.is_testing))
        self.df_horse_record = self.uploader.get_postgreSQL(\
            Constant.get_rds_tables_key(Constant.RDS_TABLE_HORSE_RECORD, self.is_testing))

        # print(self.df_race_info)

    def process(self) -> None:
        """
        Process the web page with Selenium. The steps are as follows:
        1. Open URL in Chrome
        2. Accept cookies
        3. Skip advertisement (if needed)
        4. Process main page and detail page
        5. Close all the window
        6. Download images (Silk)
        7. Upload raw data (JSON) and images to AWS S3, and in table format in AWS RDS

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

        print(f"Finishing scraping")
        # print(f"============================")
        # pprint.pprint(self.races)
        # print(f"============================")

        # TODO: disable if exceeds S3 free tier limit
        self.upload_s3()
        self.upload_rds()

        
        self.cleanup()
        self.print_summary()

    def restore_cache_result(self) -> None:
        """
        Restore from json file if the raw data is available
        """

        try:
            with open(self.out_path+self.out_file, "r") as f:
                race_list = json.load(f)
            
            self.races = [RacingPostRaceRecord.from_dict(race) for race in race_list]
        except FileNotFoundError as e:
            pass

    def load_url(self, wait_seconds : int = 10) -> None:
        """
        Load URL until the accept cookies button clickable

        Parameters 
        ==============
        wait_seconds : int
            The timeout interval for waiting

        """
        xpath_accept_cookies = Constant.XPATH_COOKIES

        until = self.get_EC_element_clickable(xpath=xpath_accept_cookies)
        super().load_url(wait_seconds, until)

    def skip_ads(self) -> None:
        """
        Ask Chrome to open the url and wait the accept cookies button appear
        """
        # skip ads
        self.click_button(xpath=Constant.XPATH_AD_BUTTON)

    def accept_cookies(self) -> None:
        """
        Accept cookies
        """
        # accept cookies
        self.click_button(xpath=Constant.XPATH_COOKIES)
        print("Accept cookies")
        
        time.sleep(2)

    def process_main_page(self) -> None:
        """
        Process the main page to get a list of detail page, and go into every valid detail page 
        """

        until = self.get_EC_element_presence(xpath=Constant.XPATH_TIME_LIST)
        self.wait_until(until)

        self.move_to_element(xpath=Constant.XPATH_TIME_LIST)

        # get a list of result item view
        timeView_list = self.get_web_element(xpath=Constant.XPATH_TIME_LIST)
        elements = self.get_web_elements(parent=timeView_list, xpath=Constant.XPATH_TIME_ITEM)

        races = []

        # print(df_race_info)

        if elements:
            print(f"{len(elements)} races found")
            elements.reverse()

            # for each result, click the full result button to go to detail view            
            for element in elements:
                full_result_button = self.get_web_element(parent=element, xpath=Constant.XPATH_FULL_RESULT)
                url = full_result_button.get_attribute("href") if full_result_button else None

                if not full_result_button or not url:
                    # imcompleted result, skip this record
                    continue
                
                if self.df_race_info is not None and self.df_race_info.shape[0] > 0:
                    df_same_url = self.df_race_info[self.df_race_info["url"] == url]

                    if df_same_url.shape[0] > 0:
                        # remove previous records from pd.Dataframe
                        if self.force_capture:
                            # print(df_same_url)
                            race_id = df_same_url["race_id"].iloc[0]

                            self.df_race_info = self.df_race_info[self.df_race_info["url"] != url]
                            self.df_prize_info = self.df_prize_info[self.df_prize_info["race_id"] != race_id]
                            self.df_horse_record = self.df_horse_record[self.df_horse_record["race_id"] != race_id]
                    
                        else:
                            print(f"This race {url} is already downloaded")
                            continue

                success, _ = self.click_button(parent=element, xpath=Constant.XPATH_FULL_RESULT)
                if not success: 
                    continue

                race_info_dict = self.process_detail_page(url)
                races.append(race_info_dict)

                # close and move to the window of the main page
                self.close_current_window()
                self.switch_to_new_window()

                # randomly sleep to avoid being suspicious 
                sleep_second = random.randint(5, 10)
                time.sleep(sleep_second)

                #TODO: TESTING
                # if len(races) == 1:
                #     break

        self.races = races

    def process_detail_page(self, url : str, move_to_new_window : bool = True) -> RacingPostRaceRecord:
        """
        Process the detail page for all the information, 
        if the detail page is shown in a new window, it will wait until a new window opened

        Parameters
        ------------
        url: str
            The URL of the detail page
        
        move_to_new_window: bool
            Whether the detail page is appear in a new window. Default value : True

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

        until = self.get_EC_element_presence(xpath=Constant.XPATH_RESULT_SECTION)
        self.wait_until(until)
        
        # race information (header labels)
        race_info = self.get_web_element(xpath=Constant.XPATH_RESULT_RACE_INFO)

        race_time = self.get_web_element(parent=race_info, xpath=Constant.XPATH_RESULT_RACE_TIME)
        race_course = self.get_web_element(parent=race_info, xpath=Constant.XPATH_RESULT_RACE_COURSE)
        race_date = self.get_web_element(parent=race_info, xpath=Constant.XPATH_RESULT_RACE_DATE)

        race_detail = self.get_web_element(parent=race_info, xpath=Constant.XPATH_RESULT_RACE_DETAIL)

        race_title = self.get_web_element(parent=race_detail, xpath=Constant.XPATH_RESULT_RACE_TITLE)

        race_detail_container = self.get_web_element(parent=race_detail, xpath=Constant.XPATH_RESULT_RACE_DETAIL_CONTAINER)
        race_rating = self.get_web_element(parent=race_detail_container, xpath=Constant.XPATH_RESULT_RACE_RATING)
        race_distance = self.get_web_element(parent=race_detail_container, xpath=Constant.XPATH_RESULT_RACE_DISTANCE)
        race_class = self.get_web_element(parent=race_detail_container, xpath=Constant.XPATH_RESULT_RACE_CLASS)
        race_condition = self.get_web_element(parent=race_detail_container, xpath=Constant.XPATH_RESULT_RACE_CONDITION)

        race_detail_div = self.get_web_element(parent=race_detail_container, xpath=Constant.XPATH_RESULT_RACE_DETAIL_DIV)

        prize_list = race_detail_div.text.split() if race_detail_div else []
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
        horse_table = self.get_web_element(xpath=Constant.XPATH_RESULT_HORSE_TABLE)
        horse_row = self.get_web_elements(parent=horse_table, xpath=Constant.XPATH_RESULT_HORSE_ROW)

        cache_record = None

        # iterate over rows to capture the information of each horse, 
        # each row may be either horse information, comment or separator, 
        # we process main and comment rows only
        for row in horse_row:
            row_class = row.get_attribute(Constant.ATTRIBUTE_CLASS)

            # main row
            if Constant.XPATH_RESULT_HORSE_TABLE_MAIN_ROW in row_class:
                # if the main row appear again, it means it is showing information for another horse
                # put the cache record into a list
                if cache_record:
                    race_info.horse_rank.append(cache_record)
                
                cache_record = RacingPostHorseRecord()

                # the first td doesn't come with a class, capture the inner div directly
                horse_pos_div = self.get_web_element(parent=row, xpath=Constant.XPATH_RESULT_HORSE_POS_DIV)

                horse_pos = self.get_web_element(parent=horse_pos_div, xpath=Constant.XPATH_RESULT_HORSE_POS)
                horse_draw = self.get_web_element(parent=horse_pos_div, xpath=Constant.XPATH_RESULT_HORSE_DRAW)

                horse_length = self.get_web_element(parent=horse_pos_div, xpath=Constant.XPATH_RESULT_HORSE_LENGTH)

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
                main_row_tds = self.get_web_elements(parent=row, xpath=Constant.XPATH_RESULT_MAIN_ROW_TDS)

                for td in main_row_tds:
                    td_class = td.get_attribute(Constant.ATTRIBUTE_CLASS)

                    if Constant.XPATH_RESULT_HORSE_TABLE_TD_HORSE_CELL in td_class:
                        horse_cell_div = self.get_web_element(parent=td, xpath=Constant.XPATH_RESULT_HORSE_CELL_DIV)

                        horse_info = self.get_web_element(parent=horse_cell_div, xpath=Constant.XPATH_RESULT_HORSE_INFO)

                        horse_no = self.get_web_element(parent=horse_info, xpath=Constant.XPATH_RESULT_HORSE_NO)
                        horse_name = self.get_web_element(parent=horse_info, xpath=Constant.XPATH_RESULT_HORSE_NAME)

                        horse_name_children = self.get_web_elements(parent=horse_name, xpath=Constant.XPATH_RESULT_HORSE_NAME_CHILDREN)
                        horse_name_text = None

                        # get rid of child element containing unused title
                        if horse_name:
                            horse_name_text = horse_name.text

                            for child in horse_name_children:
                                horse_name_text = horse_name_text.replace(child.text, "")

                        horse_country = self.get_web_element(parent=horse_info, xpath=Constant.XPATH_RESULT_HORSE_COUNTRY)
                        horse_odd = self.get_web_element(parent=horse_info, xpath=Constant.XPATH_RESULT_HORSE_ODD)

                        # for silk, capture the url only, will start downloading the images after capturing all races
                        horse_silk = self.get_web_element(parent=horse_cell_div, xpath=Constant.XPATH_RESULT_HORSE_SILK)

                        cache_record.horse_no = horse_no.text if horse_no else None
                        cache_record.horse_name = horse_name_text
                        cache_record.horse_country = horse_country.text if horse_country else None
                        cache_record.horse_odd = horse_odd.text if horse_odd else None

                        # we only save the silk for the winner
                        if horse_pos_text == "1":
                            cache_record.horse_silk_url = horse_silk.get_attribute("src") if horse_silk else None
                        
                        horse_human = self.get_web_element(parent=horse_info, xpath=Constant.XPATH_RESULT_HORSE_HUMAN)
                        horse_human_wrapper = self.get_web_elements(parent=horse_human, xpath=Constant.XPATH_RESULT_HORSE_HUMAN_WRAPPER)
            
                        for wrapper in horse_human_wrapper:
                            prefix = wrapper.get_attribute(Constant.ATTRIBUTE_DATA_PREFIX)
                            if Constant.XPATH_RESULT_HORSE_JOCKEY_PREFIX in prefix:
                                horse_jockey = self.get_web_element(parent=wrapper, xpath=Constant.XPATH_RESULT_HORSE_JOCKEY)
                                cache_record.horse_jockey = horse_jockey.text if horse_jockey else None
                            elif Constant.XPATH_RESULT_HORSE_TRAINER_PREFIX in prefix:
                                horse_trainer = self.get_web_element(parent=wrapper, xpath=Constant.XPATH_RESULT_HORSE_TRAINER)
                                cache_record.horse_trainer = horse_trainer.text if horse_trainer else None

                    elif Constant.XPATH_RESULT_HORSE_TABLE_TD_AGE_CELL in td_class:
                        horse_age = td
                        cache_record.horse_age = horse_age.text if horse_age else None
                    
                    elif Constant.XPATH_RESULT_HORSE_TABLE_TD_WGT_CELL in td_class:
                        horse_wgt_span = self.get_web_elements(parent=td, xpath=Constant.XPATH_RESULT_HORSE_WGT_SPAN)
                
                        for span in horse_wgt_span:
                            span_class = span.get_attribute(Constant.ATTRIBUTE_CLASS)

                            if Constant.XPATH_RESULT_HORSE_TABLE_ST in span_class:
                                horse_st = span
                                cache_record.horse_st = horse_st.text if horse_st else None
                            elif Constant.XPATH_RESULT_HORSE_TABLE_EXTRA_DATA in span_class:
                                horse_extra_weight = self.get_web_element(parent=span, xpath=Constant.XPATH_RESULT_HORSE_EXTRA_WEIGHT)
                                cache_record.horse_extra_weight = horse_extra_weight.text if horse_extra_weight else None
                            elif Constant.XPATH_RESULT_HORSE_TABLE_HEAD_GEAR in span_class:
                                horse_head_gear = span
                                cache_record.horse_head_gear = horse_head_gear.text if horse_head_gear else None
                            elif span.get_attribute(Constant.ATTRIBUTE_DATA_TEST_SELECTOR) == Constant.ATTRIBUTE_DATA_HORSE_WEIGHT_LB:
                                horse_lb = span
                                cache_record.horse_lb = horse_lb.text if horse_lb else None

                    else:
                        data_ending = td.get_attribute(Constant.ATTRIBUTE_DATA_ENDING)

                        if data_ending and data_ending == Constant.ATTRIBUTE_DATA_ENDING_OR:
                            horse_or = td
                            cache_record.horse_or = horse_or.text if horse_or else None
                        elif data_ending and data_ending == Constant.ATTRIBUTE_DATA_ENDING_TS:
                            horse_ts = td
                            cache_record.horse_ts = horse_ts.text if horse_ts else None
                        elif data_ending and data_ending == Constant.ATTRIBUTE_DATA_ENDING_RPR:
                            horse_rpr = td
                            cache_record.horse_rpr = horse_rpr.text if horse_rpr else None
                        elif data_ending and data_ending == Constant.ATTRIBUTE_DATA_ENDING_MR:
                            horse_mr = td
                            cache_record.horse_mr = horse_mr.text if horse_mr else None

            # comment row    
            elif Constant.XPATH_RESULT_HORSE_TABLE_COMMENT_ROW in row_class:
                horse_comment = self.get_web_element(parent=row, xpath=Constant.XPATH_RESULT_HORSE_COMMENT)
                cache_record.horse_comment = horse_comment.text if horse_comment else None

        if cache_record:
            race_info.horse_rank.append(cache_record)
        
        # additional race info
        race_info_ols = self.get_web_elements(xpath=Constant.XPATH_RESULT_RACE_INFO_OLS)
        extra_infos = []

        # skip svg title for extra info
        for ol in race_info_ols:
            ol_text = ol.text
            ol_children = self.get_web_elements(parent=ol, xpath=Constant.XPATH_RESULT_OL_CHILDREN)

            for child in ol_children:
                if child.tag_name == Constant.ATTRIBUTE_TAG_SVG:
                    svg_title = child.text
                    ol_text = ol_text.replace(svg_title, "")

            extra_infos.append(ol_text)
        
        race_info.race_extra_info = "\n".join(extra_infos)

        race_info_comment = self.get_web_element(xpath=Constant.XPATH_RESULT_RACE_INFO_COMMENT)
        race_info.race_info_comment = race_info_comment.text if race_info_comment else None

        # assign the race with an UUID
        race_info.race_id = uuid.uuid5(uuid.NAMESPACE_URL, url).hex

        return race_info

    def save_raw_data(self) -> None:
        """
        Save raw data in json format. 
        It will create a folder if the folder specified in out_path doesn't exist.
        """
        os.makedirs(self.out_path, exist_ok=True)

        with open(self.out_path + self.out_file, 'w+') as file:
            json.dump([race.to_dictionary() for race in self.races], file, indent=4)

    def download_images(self) -> None:
        """
        Download images for each race and save it into image path
        """
        
        print("Downloading images...")
        for race in self.races:
            race_uuid = race.race_id
            for horse in race.horse_rank:
                horse_silk_url = horse.horse_silk_url

                if horse_silk_url:
                    if self.df_horse_record is not None and self.df_horse_record.shape[0] > 0:
                        same_silk = self.df_horse_record[self.df_horse_record["horse_silk_url"] == horse_silk_url]
                    else:
                        same_silk = None

                    if same_silk is None or same_silk.shape[0] == 0:
                        this_image_path = self.image_path + race_uuid + "/" 

                        file_name = self.download_image(horse_silk_url, this_image_path)
                        horse.horse_silk = race_uuid + "/" + file_name
                    else:
                        horse.horse_silk = same_silk["horse_silk"].iloc[0] if same_silk is not None else None


            sleep_second = random.randint(1, 5)
            time.sleep(sleep_second)

    def normalize_race_record(self, race_list : list[dict] = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Normalize the raw data into 3 tables (race information, prize information and horse records)
        Parameters
        ------------
        race_list: list[dict]
            A list for races in dictionary format

        Returns
        ------------
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            horse_info table, prize_info and horse_record table in panda DataFrame format

        """

        if not race_list:
            race_list = self.races

        race_info_dict = defaultdict(list)
        prize_info_dict = defaultdict(list)
        horse_info_dict = defaultdict(list)
       
        for race in race_list:
            race_dict = race.to_dictionary()
            race_id = race_dict["race_id"]
            
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

        df_race_info = pd.DataFrame.from_dict(race_info_dict).set_index("race_id")
        df_prize_info = pd.DataFrame.from_dict(prize_info_dict).set_index(["race_id", "rank"])
        df_horse_info = pd.DataFrame.from_dict(horse_info_dict).set_index(["race_id", "horse_rank", "horse_name"])

        # print(df_horse_info)

        return df_race_info, df_prize_info, df_horse_info

    def upload_s3(self) -> None:
        """
        Upload images and raw data file into s3. The key for raw data will be equal to raw_data/{input filename}
        and for images will be {UUID for each race}/{horse_silk}
        """

        # for testing only
        if not self.races:
            self.restore_cache_result()

        if len(self.races) > 0:
            # upload images into s3
            for race in self.races:
                race_id = race.race_id

                for horse in race.horse_rank:
                    if horse.horse_silk_url:
                        if self.df_horse_record is not None and self.df_horse_record.shape[0] > 0:
                            df_same_silk = self.df_horse_record[self.df_horse_record["horse_silk_url"] == horse.horse_silk_url]
                            url = df_same_silk["horse_silk_url_s3"].iloc[0] if df_same_silk.shape[0] > 0 else None
                        else:
                            df_same_silk = None
                            url = None
                        
                        file_name = horse.horse_silk

                        if url and not self.force_capture:
                            horse.horse_silk_url_s3 = url
                        elif file_name:
                            keyname = file_name
                            silk_url = self.uploader.upload_to_s3(f"{self.image_path}{keyname}", keyname)
                            horse.horse_silk_url_s3 = silk_url

            
            self.save_raw_data()

            # upload raw data into s3
            self.uploader.upload_to_s3(f"{self.out_path + self.out_file}", f"raw_data/{self.out_file}")
                            
    def upload_rds(self) -> None:
        """
        Upload raw data into tabular format into AWS RDS, it first normalize raw data into 3 tables
        (race_info, prize_info and horse_record) in pandas dataframe format, where prize info and 
        horse record has the foreign key "race_id" referencing to primary key "race_id" in race_info 
        table. 
        """
        
        if not self.races:
            self.restore_cache_result()

        if len(self.races) > 0:
            self.df_race_upload, self.df_prize_upload, self.df_horse_upload = self.normalize_race_record()

            if self.df_race_info is not None and self.force_capture:
                
                self.df_race_info = self.df_race_info.set_index("race_id")
                self.df_prize_info = self.df_prize_info.set_index(["race_id", "rank"])
                self.df_horse_record = self.df_horse_record.set_index(["race_id", "horse_rank", "horse_name"])

                df_race_upload = self.df_race_info.append(self.df_race_upload)
                df_prize_upload = self.df_prize_info.append(self.df_prize_upload)
                df_horse_upload = self.df_horse_record.append(self.df_horse_upload)

                if_exists = "replace"

            else:
                df_race_upload = self.df_race_upload
                df_prize_upload = self.df_prize_upload
                df_horse_upload = self.df_horse_upload

                if_exists = "replace" if self.force_capture else "append"

            self.uploader.upload_postgreSQL(df_race_upload, \
                Constant.get_rds_tables_key(Constant.RDS_TABLE_RACE_INFO, self.is_testing), if_exists)
            self.uploader.upload_postgreSQL(df_prize_upload, \
                Constant.get_rds_tables_key(Constant.RDS_TABLE_PRIZE_INFO, self.is_testing), if_exists)
            self.uploader.upload_postgreSQL(df_horse_upload, \
                Constant.get_rds_tables_key(Constant.RDS_TABLE_HORSE_RECORD, self.is_testing), if_exists)

    def cleanup(self) -> None:
        """
        Close all connections
        """

        self.uploader.close_connection()

        # try:
        #     shutil.rmtree(self.image_path)
        # except OSError as e:
        #     print("Error in removing image path: %s - %s." % (e.filename, e.strerror))

        # try:
        #     shutil.rmtree(self.out_path)
        # except OSError as e:
        #     print("Error in removing raw data path: %s - %s." % (e.filename, e.strerror))

    def print_summary(self) -> None:
        """
        Print redult summary
        """

        if len(self.races) > 0:
            print("========================")
            print(f"{self.df_race_upload.shape[0]} races scraped")
            print(f"{self.df_prize_upload.shape[0]} prize info records scraped")
            print(f"{self.df_horse_upload.shape[0]} horse records scraped")
            print("========================")
