'''
Description: This script is pulls reviews from users that rated the book 5 stars.
'''

from bs4 import BeautifulSoup
import selenium as sl
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains # to scroll to an element
from selenium.common.exceptions import NoSuchElementException

url= 'https://www.goodreads.com/book/show/60194162/reviews'
wait_time = 10
filter_button_path = '/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div[2]/div/div[1]/div[1]'

options = webdriver.ChromeOptions()
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)

driver.maximize_window()


driver.get(url)
#driver.execute_script("document.body.style.transform='scale(0.9)';")
time.sleep(10)
#driver.save_screenshot('after_outzoom.png')


filter_button = driver.find_element(By.XPATH, filter_button_path).scroll_into_view()

actions = ActionChains(driver).move_to_element(filter_button)
driver.save_screenshot('right_before_click.png')
time.sleep(3)
filter_button.click()
dict_of_reviews = dict()


# GRABBING DATA
'''html = driver.page_source

soup = BeautifulSoup(html, "html.parser")

user_links = list()
user_ratings = list()

#list of lists
reviews = (soup.find('div', id='__next')
           .find('div', class_='PageFrame PageFrame--siteHeaderBanner')
           .find('main', class_='PageFrame__main BookReviewsPage')
           .find('div', class_='BookReviewsPage__gridContainer')
           .find('div', class_='BookReviewsPage__rightColumn')
           .find('div', class_='ReviewsList').find_all(class_= 'ReviewCard'))
print(len(reviews))
for review in reviews:
    user_links.append(review.find('a', class_ = 'Avatar Avatar--medium', href = True)['href'])

    user_ratings.append(review.find('span', class_ = 'RatingStars RatingStars__small')['aria-label'])'''


