'''
Description: Script to scrape data from goodreads bookshelf and exported as csv.
'''

from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains # to scroll to an element
from selenium.common.exceptions import NoSuchElementException

dismiss_button_xpath = '/html/body/div[3]/div/div/div[1]/button'
read_shelf_button_xpath = '/html/body/div[2]/div[3]/div[1]/div[1]/div[3]/div[5]/div[2]/div/div[1]/div[1]/a[1]'
#url = 'https://www.goodreads.com'
#session_token = '6LC1xz4hCduksSr0lzsMf2aPd00JxNav/RPDUzRgAGCQ1qHF9WUI42FznM80ed1xq2O/wv6eQsJJxhQwI2zSgcwHIQCQ85p85HnbRflIzDNFYTsTbWkSXAbosUa2Ovmp7M62sO5yc18yxUMrjYxMb9ggt2EIEDahPx4IMZNLeSStkQWKl+Kfzz6XZ0O6rM/3yKBeytr3ZRNYbE+E7aZE05mhoYCjz3T7ZBWTsy8mUAScwLK3+xsdtxlfuKS93MEYwRQoD+8N2lgvnfxdQfEOInjqKsneVEfgdh4B+7LadO/b/Z2aw5ouzOdayNnr4sVFSmlzr6JwlBg/Gqtl93VqvsRBboYnPoNzJ0EaIu51S8C6QTpDdyosTS9/zrXMKTJ8'

#options = webdriver.ChromeOptions()
#options.add_argument('--headless')

def element_exists(xpath, driver):
    '''
    Returns whether or not a given element exists
    '''
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def get_url(user_id, page_num):
    '''returns url for user given page number and user id'''
    url_beginning = 'https://www.goodreads.com/review/list/' + user_id

    url_end = '?page=' + str(page_num) + '?shelf=read'

    return url_beginning + url_end

def dismiss_popup(xpath, driver):
     '''checks if popup exists. If so, dismisses'''
     if element_exists(dismiss_button_xpath, driver):
                # click X button
                print('Exited out of ad')
                close_button = driver.find_element(By.XPATH, dismiss_button_xpath)
                ActionChains(driver).move_to_element(close_button).click().perform()
                time.sleep(4)

def get_bookshelf(user_id):
    '''
    takes a user id (str) as an argument
    Returns a dataframe of a users goodreads read shelf
    
    '''

    driver = webdriver.Chrome()
    reviews_as_dicts = list()
    page_num = 1

    # getting url of first page of user's library
    url = get_url(user_id, page_num)

    # opening page
    page = driver.get(url)
    
    driver.maximize_window()

    time.sleep(3)

    #checking for pop-up
    dismiss_popup(dismiss_button_xpath, driver)

    page_exists = True

    # extracting reviews data
    while page_exists:
        try:
            #print('Beginning page: ' + str(page_num))

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            time.sleep(4)
            bookshelf = (soup.find('div', id='bodycontainer',)
            .find('div', class_='mainContentContainer')
            .find('div', class_='mainContent')
            .find('div', class_='mainContentFloat')
            .find('div', class_='myBooksPage')
            .find('div', class_='last col')
            .find('div', class_='js-dataTooltip')
            .find('table', class_='table stacked'))

            # list of lists
            reviews = bookshelf.find_all('tr', class_= 'bookalike review')

            # quitting while loop if table is empty at nth page
            if len(reviews) == 0:
                break

            data_labels = [value.label.string for value in reviews[1].find_all('td')]
            data_labels.append('link')

            for review in reviews:
                row_data = review.find_all('td')

                # getting link 
                book_link = row_data[3].find('a', href = True)['href']

                # extracting other values from book
                for i in range(1, len(row_data)):
                    raw_value_as_text = row_data[i].text#.strip()
                    cleaned_value = raw_value_as_text.replace('\n', '')
                    cleaned_value = cleaned_value.replace(data_labels[i], '').strip()
                    row_data[i] = cleaned_value

                # adding link to book data
                row_data.append(book_link)

                reviews_as_dicts.append({k:v for (k,v) in zip(data_labels, row_data)})
            
            # get page functionality
            #print(str(page_num) + ' Complete!')

            # getting next page
            page_num = page_num + 1

            if page_num % 10 == 0:
                 time.sleep(10)

            url = get_url(user_id, page_num)

            page = driver.get(url)

        except Exception as e: 
            if requests.get(url).status_code == '200':
                 page_exists = False
            elif element_exists(dismiss_button_xpath, driver):
                # click X button
                #print('Exited out of ad')
                close_button = driver.find_element(By.XPATH, dismiss_button_xpath)
                ActionChains(driver).move_to_element(close_button).click().perform()
                time.sleep(4)
            else:
                print('Unable to get to page ' + str(i) + ' of reviews.')
                driver.save_screenshot('error shot.png')
                print(e)
                break

    # converting to dataframe
    df = pd.DataFrame(reviews_as_dicts)

    #print(df.info())

    driver.close()
    # saving data
    path = 'user_libraries/' + user_id + '_bookshelf_data.csv'
    df.to_csv(path)

    #print(re.search('<div class="value">(.*)<div', books[1]).group())

    #reviews = {review_id: book for (review_id, book) in zip(review_ids, books)}
    # converting list of fields to a dictionary for each book
    #books = [for book in books]

#user_id = '8300563'

#get_bookshelf(user_id)