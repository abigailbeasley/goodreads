'''
Description: This script is intended pulls urls and ratings of the top reviews of a book.
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

def element_exists(xpath, driver):
    '''
    Returns whether or not a given element exists
    '''
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def load_reviews(n, url, wait_time: int = 10):
    '''
    This function loads reviews for a Goodreads book page
    Inputs:
    - n: the number of pages of reviews to load
    - url: the URL of the desired Goodreads page for which reviews
    - wait_time: specifies the number of seconds to wait for a page to load after an action
    shoul be loaded from
    Returns: the page source for the webpage after loading the desired
    number of pages of reviews.
    '''

    #second_load_button_xpath = '/html/body/div[1]/div[2]/main/div[1]/div[2]/div[4]/div[5]/div/button/span[2]'
    #first_load_button_xpath = '/html/body/div[1]/div[2]/main/div[1]/div[2]/div[3]/div/div[5]/div[4]/a/span[1]'
    first_load_button_xpath = '/html/body/div[1]/div[2]/main/div[1]/div[2]/div[4]/div[4]/div/button/span[1]'
    close_button_xpath = '/html/body/div[3]/div/div[1]/div/div/button'
    whole_overlay_path = '/html/body/div[3]'
    first_page_height_subtraction = 2500
    headless_first_page_subtraction = 1900
   
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)

    driver.get(url)
    driver.maximize_window()

    time.sleep(wait_time)

    # initial click
    i = 1
    while True and i < 2:
        # intial scroll height
        scroll_height = driver.execute_script('return document.body.scrollHeight')# - headless_first_page_subtraction
        try:
            driver.execute_script("window.scrollTo(0, " + str(scroll_height) + ");")
            time.sleep(wait_time)
            button = driver.find_element(By.XPATH, first_load_button_xpath)
            ActionChains(driver).move_to_element(button).click().perform()
            time.sleep(wait_time)
            i = i+1
        except Exception as e:
            if element_exists(whole_overlay_path, driver):
                # click X button
                #print('Exited out of ad')
                close_button = driver.find_element(By.XPATH, close_button_xpath)
                ActionChains(driver).move_to_element(close_button).click().perform()
            else:
                driver.save_screenshot('error shot.png')
                print(e)
                break
    
        while True and i <= n:
            scroll_height = driver.execute_script('return document.body.scrollHeight')
            try:
                driver.execute_script("window.scrollTo(0, " + str(scroll_height) + ");")
                time.sleep(wait_time)
                button = driver.find_element(By.XPATH, first_load_button_xpath)
                ActionChains(driver).move_to_element(button).click().perform()
                time.sleep(wait_time)
                i = i+1
            except Exception as e:
                if element_exists(whole_overlay_path, driver):
                    # click X button
                    print('Exited out of ad')
                    close_button = driver.find_element(By.XPATH, close_button_xpath)
                    ActionChains(driver).move_to_element(close_button).click().perform()
                else:
                    print('Unable to get to page ' + str(i) + ' of reviews.')
                    driver.save_screenshot('error shot.png')
                    print(e)
                    break
    time.sleep(wait_time)

    return driver.page_source

def grab_reviewers_and_ratings(html):
    '''
    This function parses html to extract reveiewer info. It takes a page_source as an input and
    It returns a pandas dataframe containing the url to the author's page as well as the
    author's rating for each review.
    '''

    soup = BeautifulSoup(html, "html.parser")

    user_links = list()
    user_ratings = list()
    user_reviews = list()

    #list of lists
    reviews = (soup.find('div', id='__next')
            .find('div', class_='PageFrame PageFrame--siteHeaderBanner')
            .find('main', class_='PageFrame__main BookReviewsPage')
            .find('div', class_='BookReviewsPage__gridContainer')
            .find('div', class_='BookReviewsPage__rightColumn')
            .find('div', class_='ReviewsList').find_all(class_= 'ReviewCard'))
    i = 1
    for review in reviews:
        print(i)
        try:
            user_links.append(review.find('a', class_ = 'Avatar Avatar--medium', href = True)['href'])
        except:
            user_links.append('no user info')
        try:
            user_ratings.append(review.find('div', class_ = 'ShelfStatus').find('span', class_ = 'RatingStars RatingStars__small')['aria-label'])
        except:
            user_ratings.append('No Rating')
        try:
            user_reviews.append(review.find('section', class_ = 'ReviewCard__content').find('span', class_='Formatted').text)
        except:
            user_reviews.append('No review text')

        i = i + 1
    data = pd.DataFrame({'user_links': user_links, 'user_ratings': user_ratings, 'review_text': user_reviews})

    return data

url = 'https://www.goodreads.com/en/book/show/60194162' + '/reviews'

page = load_reviews(10, url, 5)

reviews = grab_reviewers_and_ratings(page)

reviews.to_csv('demon_copperhead_review_info.csv')

