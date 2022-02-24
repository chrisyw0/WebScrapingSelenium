import stat
import pytest
from racing_post_scraper import RacingPostFastResult
import os
import json
import re
from datetime import date, timedelta
import string

CORRECTNESS_TEST_URL = "https://www.racingpost.com/results/2022-02-21/time-order/"
CORRECTNESS_RAW_DATA_FILE = "20220221.json"

yesterday = date.today() - timedelta(days=1)

FORMAT_TEST_URL = f"https://www.racingpost.com/results/{yesterday.strftime('%Y-%m-%d')}/time-order/"
FORMAT_RAW_DATA_FILE = f"{yesterday.strftime('%Y%m%d')}.json"

IMAGE_PATH = "./images/"
RAW_DATA_PATH = "./raw_data/"

@pytest.fixture()
def fast_result_correctness():
    return RacingPostFastResult(CORRECTNESS_TEST_URL, IMAGE_PATH, RAW_DATA_PATH, CORRECTNESS_RAW_DATA_FILE)

@pytest.fixture()
def fast_result_format():
    return RacingPostFastResult(FORMAT_TEST_URL, IMAGE_PATH, RAW_DATA_PATH, FORMAT_RAW_DATA_FILE)

class TestRacingPostResult():
    @staticmethod
    def assert_dict_value(key_value_dict, key, value):
        assert key in key_value_dict, f"Key {key} is not in the dictionary {key_value_dict}"

        if type(key_value_dict[key]) == str:
            assert key_value_dict[key].strip() == value, f"dict[{key}] = {key_value_dict[key].strip()} not equal to desire value {value}."
        else:
            assert key_value_dict[key] == value, f"dict[{key}] = {key_value_dict[key]} not equal to desire value {value}."

    @staticmethod
    def assert_dict_subvalue(key_value_dict, key, subvalue):
        assert key in key_value_dict, f"Key {key} is not in the dictionary {key_value_dict}"
        assert subvalue in key_value_dict[key].strip(), f"Desire value {subvalue} not found in dict[{key}] = {key_value_dict[key].strip()}."

    @staticmethod
    def assert_list_length(key_value_dict, key, length):
        assert key in key_value_dict, f"Key {key} is not in the dictionary {key_value_dict}"
        assert len(key_value_dict[key]) == length, f"List length {len(key_value_dict[key])} not equal to desired value {length}"

    @staticmethod
    def assert_dict_value_format(key_value_dict, key, allow_empty=False, valid_chars=None, regex_pattern=None):
        assert key in key_value_dict, f"Key {key} is not in the dictionary {key_value_dict}"
        assert type(key_value_dict[key]) == str, f"Value type {type(key_value_dict[key])} is not equal to string"

        if not allow_empty:
            assert len(key_value_dict[key].strip()) > 0, f"Empty value for Key {key} {key_value_dict[key].strip()}"

        is_empty = len(key_value_dict[key].strip()) == 0 
        if is_empty and allow_empty:
            return

        if valid_chars:
            assert set(key_value_dict[key].strip()) <= set(valid_chars), f"Value for key contains invalid chars {key_value_dict[key].strip()}, valid chars {valid_chars}"

        if regex_pattern:
            assert re.search(regex_pattern, key_value_dict[key].strip()), f"Value for key contains invalid pattern {key_value_dict[key].strip()}, valid pattern {regex_pattern}"

    def test_correctness(self, fast_result_correctness):
        fast_result_correctness.process()

        assert os.path.exists(IMAGE_PATH) == True, f"Image path {IMAGE_PATH} isn't existed"
        assert os.path.exists(RAW_DATA_PATH + CORRECTNESS_RAW_DATA_FILE) == True, f"Raw data path {RAW_DATA_PATH + CORRECTNESS_RAW_DATA_FILE} isn't existed"

        with open(RAW_DATA_PATH + CORRECTNESS_RAW_DATA_FILE, "r") as f:
            race_list = json.load(f)

        assert len(race_list) == 23, f"Number of race {len(race_list)} not equal to 23"
        assert type(race_list) == list, f"Race list type {type(race_list)} is not a list"

        first_race = race_list[0]

        self.assert_dict_value(first_race, "time", "7:30")
        self.assert_dict_value(first_race, "date", "21 Feb 2022")
        self.assert_dict_value(first_race, "course", "Newcastle (AW)")
        self.assert_dict_value(first_race, "title", "Betway Novice Stakes (GBB Race)")
        self.assert_dict_value(first_race, "rating", "(3yo+)")
        self.assert_dict_value(first_race, "condition", "Standard To Slow")
        self.assert_dict_value(first_race, "class", "(Class 5)")
        self.assert_dict_value(first_race, "distance", "5f")
        
        self.assert_list_length(first_race, "prize", 4)

        assert first_race["prize"][0] == {"1st": "£3,942"}, f"1st rank prize {first_race['prize'][0]} is not equal to 1st £3,942"
        assert first_race["prize"][1] == {"2nd": "£1,850.55"}, f"2nd rank prize {first_race['prize'][1]} is not equal to 2nd £1,850.55"
        assert first_race["prize"][2] == {"3rd": "£925.64"}, f"3rd rank prize {first_race['prize'][2]} is not equal to 3rd £925.64"
        assert first_race["prize"][3] == {"4th": "£462.82"}, f"4th rank prize {first_race['prize'][3]} is not equal to 4th £462.82"

        self.assert_list_length(first_race, "horse_rank", 6)

        third_horse = first_race["horse_rank"][2]

        self.assert_dict_value(third_horse, "horse_rank", "3")
        self.assert_dict_value(third_horse, "horse_draw", "7")
        self.assert_dict_value(third_horse, "horse_length", "½ [4¼]")
        self.assert_dict_value(third_horse, "horse_no", "7.")
        self.assert_dict_value(third_horse, "horse_name", "Red How")
        self.assert_dict_value(third_horse, "horse_country", "") 
        self.assert_dict_value(third_horse, "horse_odd", "20/1")
        self.assert_dict_value(third_horse, "horse_jockey", "Joanna Mason")
        self.assert_dict_value(third_horse, "horse_trainer", "Julie Camacho")
        self.assert_dict_value(third_horse, "horse_age", "3")
        self.assert_dict_value(third_horse, "horse_st", "8")
        self.assert_dict_value(third_horse, "horse_lb", "6")
        self.assert_dict_value(third_horse, "horse_or", "–")
        self.assert_dict_value(third_horse, "horse_ts", "16")
        self.assert_dict_value(third_horse, "horse_rpr", "44")
        self.assert_dict_value(third_horse, "horse_mr", "–")
        self.assert_dict_value(third_horse, "horse_comment", "Slowly away, in rear, shaken up 2f out, ridden and headway over 1f out, kept on inside final furlong, not pace to challenge (op 16/1)")
        self.assert_dict_value(third_horse, "horse_slik_url", "https://www.rp-assets.com/svg/5/6/7/298765.svg")

        self.assert_dict_subvalue(first_race, "race_extra_info", " ran Off time: 7:30:34 Winning time: 1m 1.27s (slow by 3.67s) Total SP: 114%")
        self.assert_dict_subvalue(first_race, "race_extra_info", "Non-runners: Flaming Dawn (self certificate)")
        self.assert_dict_subvalue(first_race, "race_extra_info", "1st owner: Saeed Manana (High Velocity)  1st breeder: Mountarmstrong Stud")
        self.assert_dict_subvalue(first_race, "race_extra_info", "2nd owner: Hughes Bros Construction Ltd (Top Notch Tommy)")
        self.assert_dict_subvalue(first_race, "race_extra_info", "3rd owner: G B Turnbull Ltd & Julie Camacho (Red How)")
        self.assert_dict_subvalue(first_race, "race_extra_info", "Tote win: £1.19 PL: £1.10 £3.70 Ex: £4.30 CSF: £4.16 Trifecta: £17.30")
        
        uuid = first_race["UUID"]

        assert os.path.exists(IMAGE_PATH+uuid+"/298765.svg") == True, f"Path for slik is not existed {IMAGE_PATH+uuid+'/298765.svg'}"

    def test_format(self, fast_result_format):
        fast_result_format.process()

        assert os.path.exists(IMAGE_PATH) == True, f"Image path {IMAGE_PATH} isn't existed"
        assert os.path.exists(RAW_DATA_PATH + FORMAT_RAW_DATA_FILE) == True, f"Raw data path {RAW_DATA_PATH + FORMAT_RAW_DATA_FILE} isn't existed"

        with open(RAW_DATA_PATH + CORRECTNESS_RAW_DATA_FILE, "r") as f:
            race_list = json.load(f)

        assert type(race_list) == list, f"Race list type {type(race_list)} is not a list"

        for race in race_list:
            assert type(race) == dict, f"Race type {type(race)} is not dictionary"

            self.assert_dict_value_format(race, "url", regex_pattern=r"https?:\/\/*")
            self.assert_dict_value_format(race, "time", regex_pattern=r"\d{1,2}:\d{2}")
            self.assert_dict_value_format(race, "date")
            self.assert_dict_value_format(race, "title")
            self.assert_dict_value_format(race, "course")
            self.assert_dict_value_format(race, "rating", allow_empty=True)
            self.assert_dict_value_format(race, "distance", allow_empty=True)
            self.assert_dict_value_format(race, "condition", allow_empty=True)
            self.assert_dict_value_format(race, "UUID")

            prize_info = race["prize"]
            for i in range(len(prize_info)):
                prize_dict = prize_info[i]
                key, value = list(prize_dict.items())[0]

                assert re.match(r"\d{0,}(1st|2nd|3rd|th)", key), f"Prize info key {key} is not match valid format"

                # ignore the currency sign
                assert re.match(r"[0-9,.]+", value[1:]), f"Prize info value {value} is not matched valid format"

            horse_rank = race["horse_rank"]
            assert type(horse_rank) == list, f"Horse list type {type(horse_rank)} is not list"
            
            for horse in horse_rank:
                assert type(horse) == dict, f"Horse type {type(horse)} is not dictionary"

                self.assert_dict_value_format(horse, "horse_rank", regex_pattern=r"\d{1,}|UR|PU|F|RO")
                self.assert_dict_value_format(horse, "horse_draw", allow_empty=True, regex_pattern=r"\d{1,}")
                self.assert_dict_value_format(horse, "horse_length", allow_empty=True)
                self.assert_dict_value_format(horse, "horse_name")
                self.assert_dict_value_format(horse, "horse_no", allow_empty=True, regex_pattern=r"\d{1,}\.")
                self.assert_dict_value_format(horse, "horse_jockey", allow_empty=True)
                self.assert_dict_value_format(horse, "horse_trainer", allow_empty=True)
                self.assert_dict_value_format(horse, "horse_age", allow_empty=True, regex_pattern=r"\d{1,}")
                self.assert_dict_value_format(horse, "horse_st", allow_empty=True, regex_pattern=r"\d{1,}")
                self.assert_dict_value_format(horse, "horse_lb", allow_empty=True, regex_pattern=r"\d{1,}")
                self.assert_dict_value_format(horse, "horse_comment", allow_empty=True)
                self.assert_dict_value_format(horse, "horse_name")
                self.assert_dict_value_format(horse, "horse_or", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_dict_value_format(horse, "horse_ts", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_dict_value_format(horse, "horse_rpr", allow_empty=True, regex_pattern=r"[\d–]+")
                self.assert_dict_value_format(horse, "horse_mr", allow_empty=True, regex_pattern=r"[\d–]+")