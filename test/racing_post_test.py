import pytest
from racing_post.racing_post_scraper import RacingPostFastResult, RacingPostRaceRecord, RacingPostPrizeRecord, RacingPostHorseRecord, Constant
import os
import re
from datetime import date, timedelta
from selenium.webdriver.common.by import By
import uuid
import copy

CORRECTNESS_TEST_URL = "https://www.racingpost.com/results/2022-02-21/time-order/"
CORRECTNESS_RAW_DATA_FILE = "20220221.json"

yesterday = date.today() - timedelta(days=1)

FORMAT_TEST_URL = f"https://www.racingpost.com/results/{yesterday.strftime('%Y-%m-%d')}/time-order/"
FORMAT_RAW_DATA_FILE = f"{yesterday.strftime('%Y%m%d')}.json"

IMAGE_PATH = "./test_images" + uuid.uuid4().hex
RAW_DATA_PATH = "./test_raw_data" + uuid.uuid4().hex

@pytest.fixture(scope="module")
def fast_result_session():
    """
    Create RacingPostFastResult obj for ongoing unit test, this will check the returned value of a 
    race from a specific date and a horse record in the race.

    Returns
    ====================
    RacingPostFastResult:
        RacingPostFastResult object initialed with predefined URL and path

    """
    fast_result = RacingPostFastResult(CORRECTNESS_TEST_URL, IMAGE_PATH, RAW_DATA_PATH, CORRECTNESS_RAW_DATA_FILE, True, True)
    yield fast_result

    fast_result.stop_scraping()


@pytest.fixture(scope="function")
def fast_result_correctness():
    """
    Create RacingPostFastResult obj for correctness test, this will check the returned value of a 
    race from a specific date and a horse record in the race.

    Returns
    ====================
    RacingPostFastResult:
        RacingPostFastResult object initialed with predefined URL and path

    """
    fast_result = RacingPostFastResult(CORRECTNESS_TEST_URL, IMAGE_PATH, RAW_DATA_PATH, CORRECTNESS_RAW_DATA_FILE, True, True)
    yield fast_result

    fast_result.stop_scraping()

@pytest.fixture(scope="function")
def fast_result_format():
    """
    Create RacingPostFastResult obj for format check, this will check the returned value format of all 
    yesterdays' race, prize records and all horse records of each race.

    Returns
    ====================
    RacingPostFastResult:
        RacingPostFastResult object initialed with predefined URL and path

    """
    fast_result = RacingPostFastResult(FORMAT_TEST_URL, IMAGE_PATH, RAW_DATA_PATH, FORMAT_RAW_DATA_FILE, True, True)
    yield fast_result

    fast_result.stop_scraping()


class TestRacingPostResult():
    @staticmethod
    def assert_value(obj, key, value):
        """
        Helper class to assert whether the attribute is existed in the object, and value of the 
        attribute is equals to the desired value. It support checking attributes in any type. 

        For string, it will remove leading and trailing spaces on the checking attribute before 
        assertion. For a list, it will check whether the desired value is in the list. For others, 
        it will compare directly using ==

        Parameters
        ===============
        obj: Any
            An object that containing the value you want to check.

        key: str
            Attribute name
        
        value: Any
            Desired value

        """
        assert hasattr(obj, key), f"Attribute {key} is not in the obj {obj}"

        if type(getattr(obj, key)) == str:
            assert getattr(obj, key).strip() == value, f"Attrbute {key} = {getattr(obj, key).strip()} not equal to desire value {value}."
        elif type(getattr(obj, key)) == list:
            assert value in getattr(obj, key), f"Desire value {value} not found in list {getattr(obj, key)}."
        else:
            assert getattr(obj, key) == value, f"Attrbute {key} = {getattr(obj, key)} not equal to desire value {value}."
    
    @staticmethod
    def assert_part_value(obj, key, value):
        """
        Helper class to assert whether the attribute is existed in the object, and value of the 
        attribute has part of the desired value. It support checking string attributes only. 

        It will also remove the leading and trailing space for the object's attribute before assertion 

        Parameters
        ===============
        obj: Any
            An object that containing the value you want to check.

        key: str
            Attribute name
        
        value: str
            Desired value

        """

        assert hasattr(obj, key), f"Attribute {key} is not in the obj {obj}"
        assert type(getattr(obj, key)) == str, f"Value type {type(getattr(obj, key))} is not equal to string"

        assert value in getattr(obj, key).strip(), f"Desire value {value} is not found in attrbute {key} = {getattr(obj, key).strip()} ."

    @staticmethod
    def assert_list_length(obj, key, length):
        """
        Helper class to assert whether the attribute is existed in the object, the type 
        attribute is equals to list, and the length of the list is equal to the desired length. 

        Parameters
        ===============
        obj: Any
            An object that containing the value you want to check.

        key: str
            Attribute name
        
        length: str
            Desired length

        """
        assert hasattr(obj, key), f"Attribute {key} is not in the obj {obj}"
        assert type(getattr(obj, key)) == list, f"Attribute {key} is not a list"

        assert len(getattr(obj, key)) == length, f"List length {len(getattr(obj, key))} not equal to desired value {length}"

    @staticmethod
    def assert_value_format(obj, key, allow_empty=False, valid_chars=None, regex_pattern=None):
        """
        Helper class to assert whether the attribute is existed in the object, the type 
        attribute is equals to string, and the format of the attribute's value match the desired 
        pattern. The pattern can be a set of valid characters or regex pattern. You can also 
        set allow empty option to check whether the value is empty

        Parameters
        ===============
        obj: Any
            An object that containing the value you want to check.

        key: str
            Attribute name
        
        length: str
            Desired length

        """

        assert hasattr(obj, key), f"Attribute {key} is not in the obj {obj}"

        if not allow_empty:
            assert type(getattr(obj, key)) == str, f"Value type {type(getattr(obj, key))} is not equal to string"
            assert len(getattr(obj, key).strip()) > 0, f"Empty value for Key {key} {getattr(obj, key).strip()}"

        is_empty = not getattr(obj, key) or len(getattr(obj, key).strip()) == 0 

        if is_empty and allow_empty:
            return

        if valid_chars:
            assert set(getattr(obj, key).strip()) <= set(valid_chars), f"Value for key contains invalid chars {getattr(obj, key).strip()}, valid chars {valid_chars}"

        if regex_pattern:
            assert re.search(regex_pattern, getattr(obj, key).strip()), f"Value for key contains invalid pattern {getattr(obj, key).strip()}, valid pattern {regex_pattern}"

    # Unit test
    def test_attributes(self, fast_result_session):
        self.assert_value(fast_result_session, "url", CORRECTNESS_TEST_URL)
        self.assert_value(fast_result_session, "image_path", IMAGE_PATH + "/")
        self.assert_value(fast_result_session, "out_path", RAW_DATA_PATH + "/")
        self.assert_value(fast_result_session, "out_file", CORRECTNESS_RAW_DATA_FILE)

    def test_load_url(self, fast_result_session):
        fast_result_session.load_url()
        self.assert_value(fast_result_session.driver, "current_url", CORRECTNESS_TEST_URL)

    def test_accept_cookies(self, fast_result_session):
        if len(fast_result_session.driver.find_elements(By.XPATH, "//*[@id=\"truste-consent-button\"]")) > 0:
            fast_result_session.accept_cookies()
            assert len(fast_result_session.driver.find_elements(By.XPATH, "//*[@id=\"truste-consent-button\"]")) == 0, \
                "Cookies button is still existed in the website"

    def test_skip_ads(self, fast_result_session):
        if len(fast_result_session.driver.find_elements(By.XPATH, "//button[contains(@class, 'ab-close-button')]")) > 0:
            fast_result_session.skip_ads()
            assert len(fast_result_session.driver.find_elements(By.XPATH, "//button[contains(@class, 'ab-close-button')]")) == 0, \
                "Ads button is still existed in the website"

    @pytest.mark.timeout(3600)
    def test_process_scraping(self, fast_result_session):
        fast_result_session.process_main_page()

        assert hasattr(fast_result_session, "races"), "Result not set after scraping"
        assert type(getattr(fast_result_session, "races")) == list, "Result is not in type list"

        for race in fast_result_session.races:
            assert isinstance(race, RacingPostRaceRecord), "Result is not in type RacingPostRaceRecord"
            assert isinstance(race.prize, RacingPostPrizeRecord), "Prize is not in type RacingPostPrizeRecord"
            assert type(race.horse_rank) == list, "Horse rank is not in type list"

            for horse in race.horse_rank:
                assert isinstance(horse, RacingPostHorseRecord), "Horse is not in type RacingPostHorseRecord"

    def test_download_images(self, fast_result_session):
        fast_result_session.download_images()

        for race in fast_result_session.races:
            this_uuid = race.race_id
            for horse in race.horse_rank:
                if horse.horse_rank == "1":
                    self.assert_value_format(horse, "horse_silk")
                    assert os.path.exists(IMAGE_PATH + "/" + horse.horse_silk) == True, \
                        f"Path for silk is not existed" + f"{IMAGE_PATH}/{this_uuid}/{horse.horse_silk}"
    
    def test_upload_s3(self, fast_result_session):
        fast_result_session.upload_s3()

        for race in fast_result_session.races:
            for horse in race.horse_rank:
                if horse.horse_silk_url:
                    self.assert_value_format(horse, "horse_silk_url_s3", regex_pattern=r"https?:\/\/s3-.*")

    def test_restore_cache_result(self, fast_result_session):
        current_races = copy.deepcopy(fast_result_session.races)
        fast_result_session.restore_cache_result()

        assert current_races == fast_result_session.races

    def test_upload_rds(self, fast_result_session):
        assert Constant.get_rds_tables_key(Constant.RDS_TABLE_RACE_INFO, True) == Constant.RDS_TABLE_RACE_INFO_TEST, \
            f"Expected table name for testing {Constant.RDS_TABLE_RACE_INFO_TEST} but found {Constant.get_rds_tables_key(Constant.RDS_TABLE_RACE_INFO, True)}"

        assert Constant.get_rds_tables_key(Constant.RDS_TABLE_PRIZE_INFO, True) == Constant.RDS_TABLE_PRIZE_INFO_TEST, \
            f"Expected table name for testing {Constant.RDS_TABLE_PRIZE_INFO_TEST} but found {Constant.get_rds_tables_key(Constant.RDS_TABLE_PRIZE_INFO, True)}"

        assert Constant.get_rds_tables_key(Constant.RDS_TABLE_HORSE_RECORD, True) == Constant.RDS_TABLE_HORSE_RECORD_TEST, \
            f"Expected table name for testing {Constant.RDS_TABLE_HORSE_RECORD_TEST} but found {Constant.get_rds_tables_key(Constant.RDS_TABLE_HORSE_RECORD, True)}"

        fast_result_session.upload_rds()

        df_race_info = fast_result_session.uploader.get_postgreSQL(Constant.get_rds_tables_key(Constant.RDS_TABLE_RACE_INFO, True))
        df_prize_info = fast_result_session.uploader.get_postgreSQL(Constant.get_rds_tables_key(Constant.RDS_TABLE_PRIZE_INFO, True))
        df_horse_record = fast_result_session.uploader.get_postgreSQL(Constant.get_rds_tables_key(Constant.RDS_TABLE_HORSE_RECORD, True))

        orginal_race_size = fast_result_session.df_race_info.shape[0] if fast_result_session.df_race_info is not None else 0
        orginal_prize_size = fast_result_session.df_prize_info.shape[0] if fast_result_session.df_prize_info is not None else 0
        orginal_horse_size = fast_result_session.df_horse_record.shape[0] if fast_result_session.df_horse_record is not None else 0

        assert df_race_info.shape[0] - orginal_race_size == fast_result_session.df_race_upload.shape[0]\
            , "Races uploaded doesn't match the number of races captured"

        assert df_prize_info.shape[0] - orginal_prize_size == fast_result_session.df_prize_upload.shape[0]\
            , "Prize records uploaded doesn't match the number of prizes captured"

        assert df_horse_record.shape[0] - orginal_horse_size == fast_result_session.df_horse_upload.shape[0]\
            , "Horse records uploaded doesn't match the number of horses captured"

        assert df_race_info[df_race_info.duplicated(["url"])].shape[0] == 0, f"Race info table contains duplicated races"

    def test_save_raw_data(self, fast_result_session):
        fast_result_session.save_raw_data()

        path = RAW_DATA_PATH+"/"+CORRECTNESS_RAW_DATA_FILE
        assert os.path.exists(path), f"Raw data file is not existed {path}"

    def test_cleanup(self, fast_result_session):
        # fast_result_session.cleanup()

        # assert os.path.exists(IMAGE_PATH) == False\
        #     , f"Image path  {IMAGE_PATH} still existed after cleanup"

        # assert os.path.exists(RAW_DATA_PATH) == False\
        #     , f"Raw data path  {RAW_DATA_PATH} still existed after cleanup"
        pass

    # Integration test
    def test_correctness(self, fast_result_correctness):
        """
        Test the data correctness
        """
        fast_result_correctness.process()
        race_list = fast_result_correctness.races

        assert len(race_list) == 23, f"Number of race {len(race_list)} not equal to 23"
        assert type(race_list) == list, f"Race list type {type(race_list)} is not a list"

        first_race = race_list[-1]

        self.assert_value(first_race, "time", "7:30")
        self.assert_value(first_race, "date", "21 Feb 2022")
        self.assert_value(first_race, "course", "Newcastle (AW)")
        self.assert_value(first_race, "title", "Betway Novice Stakes (GBB Race)")
        self.assert_value(first_race, "rating", "(3yo+)")
        self.assert_value(first_race, "condition", "Standard To Slow")
        self.assert_value(first_race, "race_class", "(Class 5)")
        self.assert_value(first_race, "distance", "5f")
        
        self.assert_list_length(first_race.prize, "rank", 4)
        self.assert_list_length(first_race.prize, "prize", 4)

        self.assert_value(first_race.prize, "rank", "1st")
        self.assert_value(first_race.prize, "rank", "2nd")
        self.assert_value(first_race.prize, "rank", "3rd")
        self.assert_value(first_race.prize, "rank", "4th")

        self.assert_value(first_race.prize, "prize", "£3,942")
        self.assert_value(first_race.prize, "prize", "£1,850.55")
        self.assert_value(first_race.prize, "prize", "£925.64")
        self.assert_value(first_race.prize, "prize", "£462.82")
        
        self.assert_list_length(first_race, "horse_rank", 6)

        third_horse = first_race.horse_rank[2]

        self.assert_value(third_horse, "horse_rank", "3")
        self.assert_value(third_horse, "horse_draw", "7")
        self.assert_value(third_horse, "horse_length", "½ [4¼]")
        self.assert_value(third_horse, "horse_no", "7.")
        self.assert_value(third_horse, "horse_name", "Red How")
        self.assert_value(third_horse, "horse_country", "") 
        self.assert_value(third_horse, "horse_odd", "20/1")
        self.assert_value(third_horse, "horse_jockey", "Joanna Mason")
        self.assert_value(third_horse, "horse_trainer", "Julie Camacho")
        self.assert_value(third_horse, "horse_age", "3")
        self.assert_value(third_horse, "horse_st", "8")
        self.assert_value(third_horse, "horse_lb", "6")
        self.assert_value(third_horse, "horse_or", "–")
        self.assert_value(third_horse, "horse_ts", "16")
        self.assert_value(third_horse, "horse_rpr", "44")
        self.assert_value(third_horse, "horse_mr", "–")
        self.assert_value(third_horse, "horse_comment", "Slowly away, in rear, shaken up 2f out, ridden and headway over 1f out, kept on inside final furlong, not pace to challenge (op 16/1)")
        
        self.assert_part_value(first_race, "race_extra_info", " ran Off time: 7:30:34 Winning time: 1m 1.27s (slow by 3.67s) Total SP: 114%")
        self.assert_part_value(first_race, "race_extra_info", "Non-runners: Flaming Dawn (self certificate)")
        self.assert_part_value(first_race, "race_extra_info", "1st owner: Saeed Manana (High Velocity)  1st breeder: Mountarmstrong Stud")
        self.assert_part_value(first_race, "race_extra_info", "2nd owner: Hughes Bros Construction Ltd (Top Notch Tommy)")
        self.assert_part_value(first_race, "race_extra_info", "3rd owner: G B Turnbull Ltd & Julie Camacho (Red How)")
        self.assert_part_value(first_race, "race_extra_info", "Tote win: £1.19 PL: £1.10 £3.70 Ex: £4.30 CSF: £4.16 Trifecta: £17.30")
        

    def test_format(self, fast_result_format):
        fast_result_format.process()
        race_list = fast_result_format.races
        
        assert type(race_list) == list, f"Race list type {type(race_list)} is not a list"

        for race in race_list:
            assert isinstance(race, RacingPostRaceRecord), f"Race type {type(race)} is not RacingPostHorseRecord"
            this_uuid = race.race_id

            self.assert_value_format(race, "url", regex_pattern=r"https?:\/\/.*")
            self.assert_value_format(race, "time", regex_pattern=r"\d{1,2}:\d{2}")
            self.assert_value_format(race, "date")
            self.assert_value_format(race, "title")
            self.assert_value_format(race, "course")
            self.assert_value_format(race, "race_class", allow_empty=True)
            self.assert_value_format(race, "rating", allow_empty=True)
            self.assert_value_format(race, "distance", allow_empty=True)
            self.assert_value_format(race, "condition", allow_empty=True)
            self.assert_value_format(race, "race_id")

            prize_info = race.prize
            assert isinstance(prize_info, RacingPostPrizeRecord), f"Race type {type(prize_info)} is not RacingPostPrizeRecord"
            for i in range(len(prize_info.rank)):
                rank, prize = prize_info.rank[i], prize_info.prize[i]

                assert re.match(r"\d{0,}(1st|2nd|3rd|th)", rank), f"Prize rank {rank} is not match valid format"

                # ignore the currency sign
                assert re.match(r"[0-9,.]+", prize[1:]), f"Prize info prize {prize} is not matched valid format"

            horse_rank = race.horse_rank
            assert type(horse_rank) == list, f"Horse list type {type(horse_rank)} is not list"

            for horse in horse_rank:
                assert isinstance(horse, RacingPostHorseRecord), f"Horse record type {type(race)} is not RacingPostHorseRecord"

                self.assert_value_format(horse, "horse_rank", regex_pattern=r"\d{1,}|UR|PU|F|RO|RR|VOI")
                self.assert_value_format(horse, "horse_draw", allow_empty=True, regex_pattern=r"\d{1,}")
                self.assert_value_format(horse, "horse_length", allow_empty=True)
                self.assert_value_format(horse, "horse_name")
                self.assert_value_format(horse, "horse_no", allow_empty=True, regex_pattern=r"\d{1,}\.")
                self.assert_value_format(horse, "horse_jockey", allow_empty=True)
                self.assert_value_format(horse, "horse_trainer", allow_empty=True)
                self.assert_value_format(horse, "horse_age", allow_empty=True, regex_pattern=r"\d{1,}")
                self.assert_value_format(horse, "horse_st", allow_empty=True, regex_pattern=r"\d{1,}")
                self.assert_value_format(horse, "horse_lb", allow_empty=True, regex_pattern=r"\d{1,}")
                self.assert_value_format(horse, "horse_comment", allow_empty=True)
                self.assert_value_format(horse, "horse_silk_url", allow_empty=True, regex_pattern=r"https?:\/\/*")
                self.assert_value_format(horse, "horse_silk_url_s3", allow_empty=True, regex_pattern=r"https?:\/\/s3-.*")
                self.assert_value_format(horse, "horse_name")
                self.assert_value_format(horse, "horse_or", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_value_format(horse, "horse_ts", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_value_format(horse, "horse_rpr", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_value_format(horse, "horse_mr", allow_empty=True, regex_pattern=r"[\d–]+")