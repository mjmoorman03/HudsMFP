import time
import requests
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import date
from webdriver_manager.chrome import ChromeDriverManager


def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(' — headless')
    chrome_options.add_argument(' — no-sandbox')
    chrome_options.add_argument(' — disable-dev-shm-usage')
    chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(3)
    driver.maximize_window()

    currentDate = date.today().strftime('%y-%m-%d')

    req = getFoodData()

    mainDishCategories = ['Starch and Potatoes', 'Entrees', 'Desserts', 'Sides', 'Halal', 'Vegetables', 'Chili Bar', "Today's Soup"]

    # filter out main dishes
    mainDishes = [x for x in req if x['Menu_Category_Name'] in mainDishCategories]

    # local database
    foods = open("foods.txt", 'r+', encoding = "ISO-8859-1")
    # read it into a set for quick lookups
    foodSet = set([x.strip() for x in foods.readlines()])

    for dish in mainDishes:
            
        # check if already added
        if dish['Recipe_Print_As_Name'] in foodSet:
            continue

        # add food to local database
        foodSet.add(dish['Recipe_Print_As_Name'])
        foods.writelines(['\n' + dish['Recipe_Print_As_Name']])

        driver.get("https://www.myfitnesspal.com/food/submit")

        # login
        if driver.current_url == r'https://www.myfitnesspal.com/account/login?callbackUrl=https%3A%2F%2Fwww.myfitnesspal.com%2Ffood%2Fsubmit':
            # wait for user (me) to authenticate due to anti-bot software
            while (input("done?\n") != "Y"):
                time.sleep(3)

        # name of food and such
        brandinput = driver.find_element("xpath", '//*[@id="food_brand"]')
        descinput = driver.find_element("xpath", '//*[@id="food_description"]')
        submitinput = driver.find_element("xpath", '//*[@id="buttonPad"]/input')
        brandinput.send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, 'HUDS mmoorman')
        descinput.send_keys(dish['Recipe_Print_As_Name'])
        submitinput.click()

        # if duplicate page pops up, skip it
        if str(driver.current_url == 'https://www.myfitnesspal.com/food/duplicate'):
            driver.get('https://www.myfitnesspal.com/food/new?date=' + currentDate + '&meal=0')

        # servings
        servingSize = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/ol/li[1]/input')
        servingSize.send_keys(dish['Serving_Size'])
        servingsPer = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/ol/li[2]/input')
        servingsPer.send_keys('1')
        
        # cals
        calories = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[1]/td[2]/input')
        calories.send_keys(dish['Calories'])

        # sugar
        sugars = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[5]/td[4]/input')
        sugars.send_keys((dish['Sugars'])[:-1])

        # protein
        protein = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[6]/td[4]/input')
        protein.send_keys((dish['Protein'])[:-1])

        # fat
        fat = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[2]/td[2]/input')
        fat.send_keys((dish['Total_Fat'])[:-1])

        # carbs
        carbs = driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[1]/table/tbody/tr[3]/td[4]/input')
        carbs.send_keys((dish['Carbs'])[:-1])

        # scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # accept cookies (necessary for some reason)
        potentialCookies = driver.find_elements(By.XPATH, '//*[@id="accept_btn"]')
        if len(potentialCookies) > 0:
            potentialCookies[0].click()

        # add to public database
        driver.find_element(By.XPATH, '//*[@id="sharefood"]').click()

        # add another
        driver.find_element('xpath', '//html/body/div[3]/div/div[2]/form/div[2]/input[2]').click()
    
    print("done")


def getFoodData():
    with open('apikey.txt', 'r') as file:
        apikey = file.readline()

    auth = HTTPBasicAuth('x-api-key', apikey)

    # location id of 14 is kirkland and eliot house
    return requests.get("https://go.apis.huit.harvard.edu/ats/dining/v3/recipes?locationId=14", auth=auth).json()



if __name__ == "__main__":
    main()
