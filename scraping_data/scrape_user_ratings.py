'''
Description: This script is intended pulls urls and ratings of the top reviews of a book.
'''

from bs4 import BeautifulSoup
#import selenium as sl
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

    first_load_button_xpath = '/html/body/div[1]/div[2]/main/div[1]/div[2]/div[5]/div[4]/div/button'
    close_button_xpath = '/html/body/div[3]/div/div[1]/div/div/button'
    whole_overlay_path = '/html/body/div[3]'
   
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)

    driver.get(url)
    driver.maximize_window()

    time.sleep(wait_time)
    i = 1

    # initial click
    while i <= n:
        #print('Loading Page: ' + str(i))
        #print('webpage length: ' + str(len(driver.page_source)))
        if i == 90:
            wait_time = wait_time + 2
        # getting scroll height
        scroll_height = driver.execute_script('return document.body.scrollHeight')
        try:
            # scrolling down to bottom of page
            driver.execute_script("window.scrollTo(0, " + str(scroll_height) + ");")
            time.sleep(wait_time) # waiting for button to load
            # finding and navigating to button to click
            button = driver.find_element(By.XPATH, first_load_button_xpath)
            # clicking the button
            ActionChains(driver).move_to_element(button).click().perform()
            time.sleep(wait_time)
            i = i+1
        # handling pop-up ads
        except Exception as e: 
            if element_exists(whole_overlay_path, driver):
                # click X button
                #print('Exited out of ad')
                close_button = driver.find_element(By.XPATH, close_button_xpath)
                ActionChains(driver).move_to_element(close_button).click().perform()
            else:
                print('Unable to get to page ' + str(i) + ' of reviews.')
                driver.save_screenshot('error shot.png')
                print(e)
                break
    
    time.sleep(wait_time)
    #print('webpage length: ' + str(len(driver.page_source)))
    #print(len(driver.page_source))

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
    #print('number of reviews: ' + str(len(reviews)))
    for review in reviews:
        #print(i)
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

'''url = 'https://www.goodreads.com/book/show/44318414-the-dutch-house' + '/reviews'

page = load_reviews(10, url, 3)

print(len(page))

print('reviews loaded!')

reviews = grab_reviewers_and_ratings(page)
print('reviews saved!')
reviews.to_csv('the_dutch_house_review_info.csv')

reviews_in_csv = pd.read_csv('the_dutch_house_review_info.csv')

print('number of reviews saved:' + str(len(reviews_in_csv)))'''
