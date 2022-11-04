import time
import requests
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import date

currentDate = date.today().strftime('%y-%m-%d')

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(' — headless')
chrome_options.add_argument(' — no-sandbox')
chrome_options.add_argument(' — disable-dev-shm-usage')
chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
driver=webdriver.Chrome(r'C:/Users/Michael Moorman/Downloads/chromedriver_win32/chromedriver.exe' , options=chrome_options)
driver.implicitly_wait(3)
driver.maximize_window()

auth = HTTPBasicAuth('x-api-key', 'd56eb9Bo3zsdsM2TkMLnLhnB8E0ohb0r')
# location id of 14 is kirkland and eliot house
req = requests.get("https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?locationId=14", auth=auth).json()

mainDishCategories = ['Starch and Potatoes', 'Entrees', 'Desserts', 'Sides', 'Halal', 'Vegetables', 'Chili Bar', "Today's Soup"]

mainDishes = [x for x in req if x['Menu_Category_Name'] in mainDishCategories]

# local database
foods = open("foods.txt", 'r+')
foodSet = set([x.strip() for x in foods.readlines()])

for each in mainDishes:

    if each == mainDishes[-1]:
        print("finished")
        
    # check if already added
    if each['Recipe_Print_As_Name'] in foodSet:
        continue

    # add food to local database
    foodSet.add(each['Recipe_Print_As_Name'])
    foods.writelines(['\n' + each['Recipe_Print_As_Name']])

    driver.get("https://www.myfitnesspal.com/food/submit")

    # login
    if driver.current_url == r'https://www.myfitnesspal.com/account/login?callbackUrl=https%3A%2F%2Fwww.myfitnesspal.com%2Ffood%2Fsubmit':
        driver.find_element('xpath', '//*[@id="email"]').send_keys('mjmoorman03@gmail.com')
        time.sleep(1)
        driver.find_element('xpath', '//*[@id="password"]').send_keys('5hUAwj@zEr.au.5')
        time.sleep(1)
        driver.find_element('xpath', '//*[@id="__next"]/div/main/div/div/form/div/div[3]/button[1]').click()

    # name of food and stuff
    brandinput = driver.find_element("xpath", '//*[@id="food_brand"]')
    descinput = driver.find_element("xpath", '//*[@id="food_description"]')
    submitinput = driver.find_element("xpath", '//*[@id="buttonPad"]/input')
    brandinput.send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, 'HUDS mmoorman')
    descinput.send_keys(each['Recipe_Print_As_Name'])
    submitinput.click()

    # if duplicate page pops up, skip it
    if str(driver.current_url == 'https://www.myfitnesspal.com/food/duplicate'):
        driver.get('https://www.myfitnesspal.com/food/new?date=' + currentDate + '&meal=0')

    # servings
    servingSize = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/ol/li[1]/input')
    servingSize.send_keys(each['Serving_Size'])
    servingsPer = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/ol/li[2]/input')
    servingsPer.send_keys('1')
    
    # cals
    calories = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[1]/td[2]/input')
    calories.send_keys(each['Calories'])

    # sugar
    sugars = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[5]/td[4]/input')
    sugars.send_keys((each['Sugars'])[:-1])

    # protein
    protein = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[6]/td[4]/input')
    protein.send_keys((each['Protein'])[:-1])

    # fat
    fat = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[2]/td[2]/input')
    fat.send_keys((each['Total_Fat'])[:-1])

    # scroll to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # accept cookies
    potentialCookies = driver.find_elements(By.XPATH, '//*[@id="accept_btn"]')
    if len(potentialCookies) > 0:
        potentialCookies[0].click()

    # add to public database
    driver.find_element(By.XPATH, '//*[@id="sharefood"]').click()

    # add another
    driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[2]/input[2]').click()

