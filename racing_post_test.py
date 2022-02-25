import stat 
import pytest
from racing_post_scraper import RacingPostFastResult, RacingPostRaceRecord, RacingPostPrizeRecord, RacingPostHorseRecord
import os
import re
from datetime import date, timedelta

CORRECTNESS_TEST_URL = "https://www.racingpost.com/results/2022-02-21/time-order/"
CORRECTNESS_RAW_DATA_FILE = "20220221.json"

yesterday = date.today() - timedelta(days=1)

FORMAT_TEST_URL = f"https://www.racingpost.com/results/{yesterday.strftime('%Y-%m-%d')}/time-order/"
FORMAT_RAW_DATA_FILE = f"{yesterday.strftime('%Y%m%d')}.json"

IMAGE_PATH = "./images/"
RAW_DATA_PATH = "./raw_data/"

@pytest.fixture()
def fast_result_correctness():
    """
    Create RacingPostFastResult obj for correctness test, this will check the returned value of a 
    race from a specific date and a horse record in the race.

    Returns
    ====================
    RacingPostFastResult:
        RacingPostFastResult object initialed with predefined URL and path

    """
    return RacingPostFastResult(CORRECTNESS_TEST_URL, IMAGE_PATH, RAW_DATA_PATH, CORRECTNESS_RAW_DATA_FILE)

@pytest.fixture()
def fast_result_format():
    """
    Create RacingPostFastResult obj for format check, this will check the returned value format of all 
    yesterdays' race, prize records and all horse records of each race.

    Returns
    ====================
    RacingPostFastResult:
        RacingPostFastResult object initialed with predefined URL and path

    """
    return RacingPostFastResult(FORMAT_TEST_URL, IMAGE_PATH, RAW_DATA_PATH, FORMAT_RAW_DATA_FILE)

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

    def test_correctness(self, fast_result_correctness):
        fast_result_correctness.process()

        assert os.path.exists(IMAGE_PATH) == True, f"Image path {IMAGE_PATH} isn't existed"
        assert os.path.exists(RAW_DATA_PATH + CORRECTNESS_RAW_DATA_FILE) == True, f"Raw data path {RAW_DATA_PATH + CORRECTNESS_RAW_DATA_FILE} isn't existed"
        
        fast_result_correctness.restore_cache_result()
        race_list = fast_result_correctness.races

        assert len(race_list) == 23, f"Number of race {len(race_list)} not equal to 23"
        assert type(race_list) == list, f"Race list type {type(race_list)} is not a list"

        first_race = race_list[0]

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
        self.assert_value(third_horse, "horse_silk_url", "https://www.rp-assets.com/svg/5/6/7/298765.svg")

        self.assert_part_value(first_race, "race_extra_info", " ran Off time: 7:30:34 Winning time: 1m 1.27s (slow by 3.67s) Total SP: 114%")
        self.assert_part_value(first_race, "race_extra_info", "Non-runners: Flaming Dawn (self certificate)")
        self.assert_part_value(first_race, "race_extra_info", "1st owner: Saeed Manana (High Velocity)  1st breeder: Mountarmstrong Stud")
        self.assert_part_value(first_race, "race_extra_info", "2nd owner: Hughes Bros Construction Ltd (Top Notch Tommy)")
        self.assert_part_value(first_race, "race_extra_info", "3rd owner: G B Turnbull Ltd & Julie Camacho (Red How)")
        self.assert_part_value(first_race, "race_extra_info", "Tote win: £1.19 PL: £1.10 £3.70 Ex: £4.30 CSF: £4.16 Trifecta: £17.30")
        
        uuid = first_race.UUID

        assert os.path.exists(IMAGE_PATH+uuid+"/298765.svg") == True, f"Path for silk is not existed {IMAGE_PATH+uuid+'/298765.svg'}"

    def test_format(self, fast_result_format):
        fast_result_format.process()

        assert os.path.exists(IMAGE_PATH) == True, f"Image path {IMAGE_PATH} isn't existed"
        assert os.path.exists(RAW_DATA_PATH + FORMAT_RAW_DATA_FILE) == True, f"Raw data path {RAW_DATA_PATH + FORMAT_RAW_DATA_FILE} isn't existed"

        fast_result_format.restore_cache_result()
        race_list = fast_result_format.races
        
        assert type(race_list) == list, f"Race list type {type(race_list)} is not a list"

        for race in race_list:
            assert isinstance(race, RacingPostRaceRecord), f"Race type {type(race)} is not RacingPostHorseRecord"

            self.assert_value_format(race, "url", regex_pattern=r"https?:\/\/*")
            self.assert_value_format(race, "time", regex_pattern=r"\d{1,2}:\d{2}")
            self.assert_value_format(race, "date")
            self.assert_value_format(race, "title")
            self.assert_value_format(race, "course")
            self.assert_value_format(race, "race_class", allow_empty=True)
            self.assert_value_format(race, "rating", allow_empty=True)
            self.assert_value_format(race, "distance", allow_empty=True)
            self.assert_value_format(race, "condition", allow_empty=True)
            self.assert_value_format(race, "UUID")

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

                self.assert_value_format(horse, "horse_rank", regex_pattern=r"\d{1,}|UR|PU|F|RO|RR")
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
                self.assert_value_format(horse, "horse_name")
                self.assert_value_format(horse, "horse_or", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_value_format(horse, "horse_ts", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_value_format(horse, "horse_rpr", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_value_format(horse, "horse_mr", allow_empty=True, regex_pattern=r"[\d–]+")