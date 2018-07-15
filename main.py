import urllib
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time


#Create URLs to search by country
def create_search_url(FirstName, LastName, City, State, Province, Country, Employer, Society):
    baseUrl_search = "https://www.cfainstitute.org/community/membership/directory/pages/results.aspx?"
    params_search = {
        'FirstName': FirstName,
        'LastName': LastName,
        'City': City,
        'State': State,
        'Province': Province,
        'Country': Country,
        'Employer': Employer,
        'Society': Society        }
    search_url = baseUrl_search + urllib.parse.urlencode(params_search)
    return search_url

def search_by_country(searchCountry):
    search_list_country = create_search_url(FirstName='', LastName='', City='', State='', Province='',
                                            Country=searchCountry, Employer='', Society='')
    print(search_list_country)
    option = webdriver.ChromeOptions()
    option.add_argument('--incognito')
    browser = webdriver.Chrome(chrome_options=option)
    browser.get(search_list_country)

    timeout = 20
    try:
        #wait for pop-up to load
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.XPATH, '//button[@class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only"]')))
        #click pop-up
        browser.find_element_by_xpath('//button[contains(@class,"ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only") and @data-automation="member-directory-terms-agree"]').click()

    except TimeoutException:
        print('Did not find pop-up at page load')

    try:
        #wait for page to load
        WebDriverWait(browser, timeout).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@class="site-footer clearfix"]')))
    except TimeoutException:
        print('Timed out waiting for page to load')
        browser.quit()

    # scroll down the page
    ScrollPauseTime = 2

    # Get scroll height
    lastHeight = browser.execute_script("return document.body.scrollHeight")
    maxDesiredScrolls = 2
    counter = 0

    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(ScrollPauseTime)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == lastHeight:
            break
        elif counter == maxDesiredScrolls:
            break
        else:
            lastHeight = new_height
            counter += 1

    # find_elements_by_xpath returns an array of selenium objects.
    bs_obj = BeautifulSoup(browser.page_source, 'html.parser')
    all_contacts = bs_obj.find_all("div", class_="dr vcard")
    for contact in all_contacts:
        link = contact.find('a')['href']
        title = contact.find('a')['title']
        name = contact.find("span",class_= "dr-name fn").string
        city = contact.find('span', class_ = 'locality').string
        state = contact.find('span', class_ = 'region').string
        country = contact.find('span', class_ = 'country-name').string

        df_current = pd.DataFrame([[link, title, name, city, state, country]], columns=['link', 'title', 'Name and Designation', 'City', 'State','Country / Region'])
        directory.append(df_current)


    # use list comprehension to get the actual repo titles and not the selenium objects.
#    innerContents = [x.get_attribute('innerHTML') for x in anchorTags]
#    innerSoup = [BeautifulSoup(x, 'html.parser') for x in innerContents]

#    aTags = [x.find('a') for x in innerSoup]
#    hrefs = [x.get('href') for x in aTags]
#    lensIds = [x.get('id') for x in aTags]
#    styleCodes = [x.contents for x in aTags]

#    objs = [LensKGlasses() for i in range(len(styleCodes) - 1)]
#    for obj, styleCode, prodLink, lensId  in zip(objs, styleCodes, hrefs, lensIds):
#        setattr(obj, 'title', str(styleCode) + str(lensId))
#        setattr(obj, 'lensId', str(lensId))
#        setattr(obj, 'url', (str("https:") + str(prodLink)))

#    return objs


directory = pd.DataFrame(columns=['link', 'title', 'Name and Designation', 'City', 'State','Country / Region'])
search_by_country('USA')

#search for all countries
#output directory to a sql table
