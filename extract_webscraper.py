from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import numpy as np

def remove_characters(df, lst_from, lst_to):
    """
    This Function replaces all characters inside df given the list
    """
    for char_from, char_to in zip(lst_from, lst_to):
        df.replace(char_from, char_to, regex=True, inplace=True)
    return df

def create_pagenumbers(page_from, page_to):
    """
    Create Pagenumbers to scrape
    """
    lst_pages = [""]
    for i in range(page_from+1, page_to+1, 1):
        lst_pages.append("?pn=" + str(i))
    print(lst_pages)
    return lst_pages

def replace_missing_values_NaN(lst_data, data, lst_adress, adress):
    """
    Check if there are missing values in the scraped data and replace them with NaN values.
    """
    if len(lst_data) < 3:
        if "Zimmer" not in data:
            print("Zimmer NaN")
            lst_data.insert(0, np.NaN)
        if "m²" not in data:
            print("Fläche NaN")
            lst_data.insert(1, np.NaN)
        if "CHF" not in data:
            print("CHF NaN")
            lst_data.insert(2, np.NaN)

    if len(lst_adress) < 3:
        if "strasse" or "Strasse" not in adress:
            print("Strasse NaN")
            lst_adress.insert(0, np.NaN)
        if "Luzern" not in adress:
            print("PLZ NaN")
            lst_adress.insert(1, np.NaN)
        if "LU" not in adress:
            print("LU NaN")
            lst_adress.insert(2, np.NaN)

    return lst_adress, lst_data

def scrape_data(lst_pages, url):
    """
    Scrape the data and return a dataframe
    """
    df_all = pd.DataFrame()
    counter = 0
    for page in lst_pages:
        driver = webdriver.Chrome()
        driver.implicitly_wait(3)

        driver.get(url + page)
        print(url + page)
        print(driver)

        driver.implicitly_wait(3)
        values = driver.find_elements(by=By.CLASS_NAME,
                                      value="Box-cYFBPY.Flex-feqWzG.MetaBody-iCkzuU.kjGCpp.dCDRxm.iCAGRS")
        print(values)
        for value in values:
            data = value.find_element(by=By.CLASS_NAME, value="Box-cYFBPY.jPbvXR.Heading-daBLVV.dOtgYu").text
            adress = value.find_element(by=By.CLASS_NAME, value="AddressLine__TextStyled-eaUAMD.iBNjyG").text

            data_corr = data[:4].replace(",", ".") + data[4:]
            lst_data = data_corr.split(",")
            lst_adress = adress.split(",")

            lst_adress, lst_data = replace_missing_values_NaN(lst_data,data,lst_adress,adress
                                                              )

            df_single = pd.DataFrame(data={"Anzahl Zimmer": lst_data[0],
                                           "Flaeche [m2]": lst_data[1],
                                           "Preis [CHF]": lst_data[2],
                                           "Strasse": lst_adress[0],
                                           "Postleitzahl": lst_adress[1],
                                           "Kanton": lst_adress[2]},
                                     index=[counter]
                                     )
            counter += 1
            df_all = pd.concat([df_all, df_single], axis=0)

            print(df_all)

        driver.close()  # the you don't see the result
    return df_all

def open_page_delete_popups():

    driver = webdriver.Chrome()
    url = 'https://www.immoscout24.ch/de'
    driver.get(url)
    driver.maximize_window()

    # click away pop up window
    driver.implicitly_wait(4)
    driver.find_element(by=By.XPATH, value='//*[@id="root"]/div/main/div/div/div/div/div[2]/button').click()

    driver.find_element(by=By.XPATH,
                        value='//*[@id="root"]/div/main/div/div/section[1]/div/div[2]/div/form/div/div[2]/div[2]/button').click()

    #Scroll through windows
    time.sleep(3)
    driver.execute_script("window.scrollBy(0,1080)", "")
    time.sleep(3)
    driver.execute_script("window.scrollBy(0,1080)", "")


def main():
    lst_pages = create_pagenumbers(page_from=1, page_to=42)
    #url = "https://www.immoscout24.ch/de/immobilien/mieten/ort-luzern"
    df = scrape_data(lst_pages, url ="https://www.immoscout24.ch/de/immobilien/mieten/ort-bern")

    df = remove_characters(df = df,
                           lst_from = ["m²", '.—', 'Zimmer', 'CHF', "ä", "ü", "ö"],
                           lst_to =   [""  ,""   , ""      , ""   , "ae", "ue", "oe"]
                           )

    df.to_csv("immoscout_bern.csv")
    print(df)
    print("end")
    return df

if __name__ == "__main__":
    df = main()




