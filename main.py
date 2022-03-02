from racing_post.racing_post_scraper import RacingPostFastResult
import sys
from datetime import date, timedelta

def main(url : str, out_path : str, out_file : str, image_path : str, force_capture : bool):
    """
    Main function of racing post scraper
    Parameters
    ----------
    url: str
        the url, it can be the URL for today result (https://www.racingpost.com/fast-results/) 
        or a specific date i.e. https://www.racingpost.com/results/2022-02-21/time-order/
    out_path: str
        the file path for the raw data file
    out_file: str
        the file name for the raw data file
    image_path: str
        the path that you want to save the image
    force_capture: bool
        Should re-scrap races that has already existed in DB
    """

    print(f"Start scrapping for {url}")

    scraper = RacingPostFastResult(url, image_path, out_path, out_file, force_capture)
    scraper.process()
    
if __name__ == "__main__":
    args = sys.argv[1:]
    
    yesterday = date.today() - timedelta(days=1)

    url = args[0] if len(args) > 0 else f"https://www.racingpost.com/results/{yesterday.strftime('%Y-%m-%d')}/time-order/"
    out_file = args[1] if len(args) > 1 else f"./raw_data/{yesterday.strftime('%Y%m%d')}.json"
    image_path = args[2] if len(args) > 2 else "./images/"
    force_capture =  args[3] == 'True' if len(args) > 3 else False

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("URL should start with http:// or https://")

    out_file_paths = out_file.split('/')

    out_filename = out_file_paths[-1]
    out_file_path = out_file[:-len(out_filename)]

    main(url, out_file_path, out_filename, image_path, force_capture)