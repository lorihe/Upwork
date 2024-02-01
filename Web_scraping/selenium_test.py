
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
        except Exception as e:
            print(f"Error occurred: {e}")

    def click_distance(self):
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "filter-radius"))
        )
        distance_list = self.driver.find_element_by_id('filter-radius')
        distance_list.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="filter-radius-menu"]/li[2]')))
        option = self.driver.find_element_by_xpath('//*[@id="filter-radius-menu"]/li[2]')
        option.click()

    def get_n_jobs(self):
        try:
            n_jobs_ele = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobsearch-JobCountAndSortPane-jobCount"))
            )
            n_jobs = n_jobs_ele.text.split(' ')[0]
            return n_jobs
        except Exception as e:
            print(f"Error occurred: {e}")

    # def get_new_url(self):
    #     current_url = self.driver.current_url
    #     if self.key_loc_click():
    #         try:
    #             WebDriverWait(self.driver, 10).until(EC.url_changes(current_url))
    #             return self.driver.current_url
    #         except TimeoutException:
    #             print("Timeout waiting for URL to change. Current URL:", self.driver.current_url)
    #             return None
    #     else:
    #         print("Click action failed.")
    #         return None

    def click_page(self, page_number):
        time.sleep(2)
        try:
            buttons = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "css-227srf"))
            )
            if buttons[page_number]:
                buttons[page_number].click()
        except Exception as e:
            print(f"Error occurred: {e}")

    def get_info(self):
        job_info_page = []
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
                    has_keyword_1 = self.check_keyword(keywords_dict1)
                    has_keyword_2 = self.check_keyword(keywords_dict2)

                    job_info = {'job_title': job_title, 'company_name': company_name, 'company_url': company_url,
                                'payment': payment, 'job_type': job_type, 'job_url': job_url,
                                f'has_{keywords_dict1["category"]}': has_keyword_1,
                                f'has_{keywords_dict2["category"]}': has_keyword_2,
                                }
                    job_info_page.append(job_info)

            except Exception as e:
                print(f"Error occurred: {e}")
        except Exception as e:
            print(f"Error occurred: {e}")
        return job_info_page

    def get_basics(self):

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobsearch-JobInfoHeader-title"))
            )
            job_title_ele = self.driver.find_element(By.CLASS_NAME, "jobsearch-JobInfoHeader-title")
            job_title = job_title_ele.text.split('\n')[0]

        except Exception as e:
            print(f"Error occurred: {e}")

        try:
            company_info = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="jobsearch-ViewjobPaneWrapper"]/div/div/div/div[1]/div/div[1]/div[2]/div/div/div/div[1]/div[1]/span/a'))
            )
            company_name = company_info.text
            company_url = company_info.get_attribute('href')
        except TimeoutException:
            company_name = None
            company_url = None

        try:
            payment_ele = WebDriverWait(self.driver, 2).until(
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

        return job_title, company_name, company_url, payment, job_type

    def check_keyword(self, keywords_dict):
        has_keyword = False
        try:
            job_desc = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "jobDescriptionText"))
            )
            job_desc_text = job_desc.text
            keywords_pattern = '|'.join([re.escape(keyword) for keyword in keywords_dict['words']])
            has_keyword = re.search(keywords_pattern, job_desc_text, re.IGNORECASE) is not None

        except Exception as e:
            print(f"Error occurred: {e}")
        return has_keyword

def main(url):

    current = Scrape(url)
    current.key_loc_click()
    current.click_distance()
    # n_jobs = current.get_n_jobs()
    # n_pages = int(n_jobs.replace(',', '')) // 5

    jobs_all = []
    jobs_all += current.get_info()
    current.click_page(1)
    jobs_all += current.get_info()
    current.click_page(3)

    jobs_all += current.get_info()
    for i in range(10):
        print(i+4)
        current.click_page(4)
        jobs_all += current.get_info()

    info_df = pd.DataFrame(jobs_all)
    info_df = info_df.drop_duplicates()
    print(info_df)

    current.driver.quit()

    info_df.to_csv(f'{date_today}_{keywords_dict1["category"]}__{keywords_dict2["category"]}_2.csv', index = False)


if __name__ == "__main__":

    indeed_url = "https://www.indeed.com/"
    date_today = date.today()

    JOBKEY = "data analyst"
    LOCATION = "New York, NY"

    KEYWORDS_sport = {'category': 'sport', 'words': ["sport", "sports"]}
    KEYWORDS_python = {'category': 'python', 'words': ["python"]}

    keywords_dict1 = KEYWORDS_sport
    keywords_dict2 = KEYWORDS_python

    main(indeed_url)

#    get_job_urls()
