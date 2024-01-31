
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import date
import re

desired_width = 320
pd.set_option('display.width', desired_width)
# pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)



# options = Options()
# proxy_server_url = "149.215.113.110:70"
# options.add_argument(f'--proxy-server={proxy_server_url}')

indeed_url = "https://www.indeed.com/"

class Scrape:
    def __init__(self, url):
        self.driver = webdriver.Chrome('chromedriver/chromedriver')
        self.driver.get(url)

    def key_loc_click(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "text-input-what"))
            )
            keywords = self.driver.find_element(By.ID, "text-input-what")
            location = self.driver.find_element(By.ID, "text-input-where")

            keywords.send_keys(JOBKEY)
            location.send_keys(Keys.HOME, Keys.SHIFT, Keys.END, LOCATION)

            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "yosegi-InlineWhatWhere-primaryButton"))
            )
            submit_button.click()
            return True
        except Exception as e:
            print(f"Error occurred: {e}")
            return False

    def get_new_url(self):
        current_url = self.driver.current_url
        if self.key_loc_click():
            try:
                WebDriverWait(self.driver, 10).until(EC.url_changes(current_url))
                return self.driver.current_url
            except TimeoutException:
                print("Timeout waiting for URL to change. Current URL:", self.driver.current_url)
                return None
        else:
            print("Click action failed.")
            return None

    def get_item(self):
        elements = None
        try:
            elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "mosaic-provider-jobcards"))
            )
        except Exception as e:
            print(f"Error occurred: {e}")
        return elements

    def get_info(self):
        job_info_all = []
        try:
            job_beacons = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "job_seen_beacon"))
            )
            try:

                for e in job_beacons:
                    a_tag = e.find_element_by_tag_name('a')
                    job_url = a_tag.get_attribute('href')

                    e.click()
                    time.sleep(2)
                    job_title, company_name, company_url, payment, job_type = self.get_basics()
                    has_keyword = self.check_keyword()


                    job_info = {'job_title': job_title, 'company_name': company_name, 'company_url': company_url,
                                'payment': payment, 'job_type': job_type, f'has_{KEYWORDS}': has_keyword, 'job_url': job_url}
                    job_info_all.append(job_info)

            except WebDriverException:
                print("Element is not clickable")
        except Exception as e:
            print(f"Error occurred: {e}")
        return job_info_all

    def get_basics(self):
        try:
            job_title_ele = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobsearch-JobInfoHeader-title"))
            )
            job_title = job_title_ele.text.split('\n')[0]
            company_info = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="jobsearch-ViewjobPaneWrapper"]/div/div/div/div[1]/div/div[1]/div[2]/div/div/div/div[1]/div[1]/span/a'))
            )
            company_name = company_info.text
            company_url = company_info.get_attribute('href')

            try:
                payment_ele = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH,
                                                             '//*[@id="jobDetailsSection"]/div[2]/div[2]/span/div/div/div'))
                )
                payment = payment_ele.text
            except TimeoutException:
                payment = None

            try:
                job_type_ele = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                             '//*[@id="jobDetailsSection"]/div[3]/div[2]/ul/li/div/div'))
                )
                job_type = job_type_ele.text
            except TimeoutException:
                job_type = None

        except Exception as e:
            print(f"Error occurred: {e}")
        return job_title, company_name, company_url, payment, job_type

    def check_keyword(self):
        has_keyword = False
        try:
            job_desc = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "jobDescriptionText"))
            )
            job_desc_text = job_desc.text
            keywords_pattern = '|'.join([re.escape(keyword) for keyword in KEYWORDS])
            has_keyword = re.search(keywords_pattern, job_desc_text, re.IGNORECASE) is not None

        except Exception as e:
            print(f"Error occurred: {e}")
        return has_keyword



def get_job_urls():
    indeed_drive = Scrape(indeed_url)
    new_url = indeed_drive.get_new_url()

    scraper = Scrape(new_url)
    elements = scraper.get_item()
    if elements:
        a_tags = elements.find_elements_by_tag_name('a')
        for a_tag in a_tags:
            print(a_tag.get_attribute('href'))
    else:
        print("Item not found or error occurred.")

    scraper.driver.quit()

if __name__ == "__main__":
    time.sleep(1)
    JOBKEY = "data analyst"
    LOCATION = "New York, NY"

    KEYWORDS = ["sport", "sports"]

    date_today = date.today()

    current = Scrape(indeed_url)

    if current.key_loc_click():
        info = current.get_info()
        info_df = pd.DataFrame(info)
        print(info_df)

    current.driver.quit()

    info_df.to_csv(f'{date_today}.csv', index = False)

#    get_job_urls()
