from webscraper import WebScrapper
import sys
import pprint
import random
import time
import uuid
import json
import os
from datetime import datetime

class RacingPostFastResult(WebScrapper):
    """
    This is a class (inherent of WebScrapper) for capturing fast result for RacingPost.com
    """
    def process(self):
        """
        Process the web page with Selenium. The steps are as follows:
        1. Open URL in Chrome
        2. Skip advertisement 
        3. Accept cookies
        4. Process main page and detail page
        5. Close all the window
        6. Download images (Slik)
        7. Save data in JSON format

        This is the entry point if you want the whole process.
        """
        self.load_url()
        self.accept_cookies()

        time.sleep(10)
        self.skip_ads()

        self.process_main_page()
        self.stop_scraping()

        self.download_images()
        self.save_raw_data()

        pprint.pprint(self.races)

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
        self.click_button(element_class="ab-close-button")

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
        prize_info = []
        
        prize_list = race_detail_div.text.split()

        for i in range(int(len(prize_list)/2)):
            prize_info.append({prize_list[2*i]: prize_list[2*i+1]})

        race_info_dict = {
            'url': url,
            'time': race_time.text if race_time else None,
            'date': race_date.text if race_date else None,
            'title': race_title.text if race_title else None,
            'course': race_course.text if race_course else None,
            'rating': race_rating.text if race_rating else None,
            'distance': race_distance.text if race_distance else None,
            'class': race_class.text if race_class else None,
            'condition': race_condition.text if race_condition else None,
            'prize': prize_info
        }
        
        # horse table
        horse_table = self.get_web_element(xpath="//table[contains(@class, 'rp-horseTable__table')]")
        horse_row = self.get_web_elements(parent=horse_table, xpath="./tbody/tr")

        horse_records = []
        cache_record = {}

        # iterate over rows to capture the information of each horse, 
        # each row may be either horse information, comment or separator, 
        # we process main and comment rows only
        for row in horse_row:
            row_class = row.get_attribute("class")

            # main row
            if "rp-horseTable__mainRow" in row_class:
                # if the main row appear again, it means it is showing information for another horse
                # put the cache record into a list
                if len(cache_record) > 0:
                    horse_records.append(cache_record)
                    cache_record = {}

                # the first td doesn't come with a CSS class, capture the div directly
                horse_pos_div = self.get_web_element(parent=row, xpath="./td/div[contains(@class, 'rp-horseTable__pos')]")

                horse_pos = self.get_web_element(parent=horse_pos_div, xpath="./div/span[contains(@class, 'rp-horseTable__pos__number')]")
                horse_draw = self.get_web_element(parent=horse_pos_div, xpath="./div/span/sup[contains(@class, 'rp-horseTable__pos__draw')]")

                horse_length = self.get_web_element(parent=horse_pos_div, xpath="./div/span[contains(@class, 'rp-horseTable__pos__length')]/span")

                if horse_pos and horse_draw:
                    horse_pos_text = horse_pos.text.replace(horse_draw.text, "").strip()
                    horse_draw_text = horse_draw.text.replace("(", "").replace(")", "").strip()
                else:
                    horse_pos_text = horse_pos.text if horse_pos else None
                    horse_draw_text = horse_draw.text if horse_draw else None

                cache_record['horse_rank'] = horse_pos_text
                cache_record['horse_draw'] = horse_draw_text
                cache_record['horse_length'] = horse_length.text if horse_length else None
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

                        horse_country = self.get_web_element(parent=horse_info, xpath=".//span[contains(@class, 'rp-horseTable__horse__country')]")
                        horse_odd = self.get_web_element(parent=horse_info, xpath=".//span[contains(@class, 'rp-horseTable__horse__price')]")

                        # for silk, capture the url only, will start downloading the images after capturing all races
                        horse_silk = self.get_web_element(parent=horse_cell_div, xpath=".//img[contains(@class, 'rp-horseTable__silk')]")

                        cache_record['horse_no'] = horse_no.text if horse_no else None
                        cache_record['horse_name'] = horse_name.text if horse_name else None
                        cache_record['horse_country'] = horse_country.text if horse_country else None
                        cache_record['horse_odd'] = horse_odd.text if horse_odd else None
                        cache_record['horse_slik_url'] = horse_silk.get_attribute("src") if horse_silk else None
                        
                        horse_human = self.get_web_element(parent=horse_info, xpath="./div[contains(@class, 'rp-horseTable__human')]")
                        horse_human_wrapper = self.get_web_elements(parent=horse_human, xpath="./span[contains(@class, 'rp-horseTable__human__wrapper')]")
            
                        for wrapper in horse_human_wrapper:
                            prefix = wrapper.get_attribute("data-prefix")
                            if "J:" in prefix:
                                horse_jockey = self.get_web_element(parent=wrapper, xpath="./a[contains(@class, 'rp-horseTable__human__link')]")
                                cache_record['horse_jockey'] = horse_jockey.text if horse_jockey else None
                            elif "T:" in prefix:
                                horse_trainer = self.get_web_element(parent=wrapper, xpath="./a[contains(@class, 'rp-horseTable__human__link')]")
                                cache_record['horse_trainer'] = horse_trainer.text if horse_trainer else None

                    elif 'rp-horseTable__spanNarrow_age' in td_class:
                        horse_age = td
                        cache_record['horse_age'] = horse_age.text if horse_age else None
                    
                    elif 'rp-horseTable__wgt' in td_class:
                        horse_wgt_span = self.get_web_elements(parent=row, xpath="./span")
                
                        for span in horse_wgt_span:
                            span_class = span.get_attribute("class")

                            if 'rp-horseTable__st' in span_class:
                                horse_st = span
                                cache_record['horse_st'] = horse_st.text if horse_st else None
                            elif 'rp-horseTable__extraData' in span_class:
                                horse_extra_weight = self.get_web_element(parent=span, xpath="./span")
                                cache_record['horse_extra_weight'] = horse_extra_weight.text if horse_extra_weight else None
                            elif span.get_attribute('data-test-selector') == 'horse-weight-lb':
                                horse_lb = span
                                cache_record['horse_lb'] = horse_lb.text if horse_lb else None

                    else:
                        data_ending = td.get_attribute("data-ending")

                        if data_ending and data_ending == "OR":
                            horse_or = td
                            cache_record['horse_or'] = horse_or.text if horse_or else None
                        elif data_ending and data_ending == "TS":
                            horse_ts = td
                            cache_record['horse_ts'] = horse_ts.text if horse_ts else None
                        elif data_ending and data_ending == "RPR":
                            horse_rpr = td
                            cache_record['horse_rpr'] = horse_rpr.text if horse_rpr else None
                        elif data_ending and data_ending == "MR":
                            horse_mr = td
                            cache_record['horse_mr'] = horse_mr.text if horse_mr else None

            # comment row    
            elif "rp-horseTable__commentRow" in row_class:
                horse_comment = self.get_web_element(parent=row, xpath='./td')
                cache_record['horse_comment'] = horse_comment.text if horse_comment else None

        if len(cache_record) > 0:
            horse_records.append(cache_record)

        # safe the horse information to the dictionary
        race_info_dict["horse_rank"] = horse_records
        
        # additional race info
        race_info_ols = self.get_web_elements(xpath="//div[contains(@class, 'rp-raceInfo')]/ul/ol")
        extra_infos = []

        for ol in race_info_ols:
            extra_infos.append(ol.text)
        
        race_info_dict["extra_info"] = "\n".join(extra_infos)

        race_info_comment = self.get_web_element(xpath="//span[contains(@class, 'rp-raceInfo__comments')]")
        race_info_dict["race_info_comment"] = race_info_comment.text if race_info_comment else None

        # assign the race with an UUID
        race_info_dict["UUID"] = uuid.uuid4().hex

        return race_info_dict

    def save_raw_data(self):
        """
        Save raw data in json format. 
        It will create a folder if the folder specified in out_path doesn't exist.
        """
        os.makedirs(self.out_path, exist_ok=True)

        with open(self.out_path + self.out_file, 'w+') as file:
            json.dump(self.races, file, indent=4)

    def download_images(self):
        """
        Download images for each race and save it into image path
        """

        print("Downloading images...")
        for race in self.races:
            race_uuid = race["UUID"]
            for horse in race["horse_rank"]:
                if "horse_slik_url" in horse:
                    horse_slik_url = horse["horse_slik_url"]

                    this_image_path = self.image_path + race_uuid + "/" 

                    file_name = self.download_image(horse_slik_url, this_image_path)
                    horse['horse_silk'] = file_name

            sleep_second = random.randrange(3.0)
            time.sleep(sleep_second)

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
    out_file = args[1] if len(args) > 1 else f"./raw_data/{today.strftime('%d%m%Y')}.json"
    image_path = args[2] if len(args) > 2 else "./images/"

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("URL should start with http:// or https://")

    out_file_paths = out_file.split('/')

    out_filename = out_file_paths[-1]
    out_file_path = out_file[:-len(out_filename)]

    main(url, out_file_path, out_filename, image_path)