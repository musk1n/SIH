from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import csv
import time
import pandas as pd

def scrape_data(driver, date):
    # Load the webpage
    driver.get("https://fcainfoweb.nic.in/reports/report_menu_web.aspx")

    # Wait for the label to be clickable and then click it
    label = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='ctl00_MainContent_Rbl_Rpt_type_0']"))
    )
    label.click()

    # Select "Daily Prices" from the dropdown
    daily_prices = Select(driver.find_element(By.ID, "ctl00_MainContent_Ddl_Rpt_Option0"))
    daily_prices.select_by_visible_text("Daily Prices")

    # Convert date to string format
    date_str = date.strftime("%d/%m/%Y")

    # Enter the date in the date input field
    date_input = driver.find_element(By.ID, "ctl00_MainContent_Txt_FrmDate")
    date_input.click()
    date_input.clear()  # Clear any pre-existing text in the input field
    date_input.send_keys(date_str)
    date_input.send_keys(Keys.RETURN)

    # Wait for the table to load
    table = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "gv0"))
    )

    # Extract data from the table
    rows = table.find_elements(By.TAG_NAME, "tr")
    data = []
    for i, row in enumerate(rows):
        if i == 0:  # Skip header row and rows after the 14th state
            continue
        cols = row.find_elements(By.TAG_NAME, "td")
        data.append([col.text for col in cols])

    # Add the date to each row of data
    for row in data:
        row.append(date_str)

    return data

# Set up the WebDriver and Service
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

start_date = datetime(2023, 9, 11)  # Replace with your start date
end_date = datetime(2024, 8, 30)   # Replace with your end date
current_date = start_date

with open("combined_retail_price_data.csv", 'a', newline='') as f:
    writer = csv.writer(f)

    # Write header row based on the provided column names
    writer.writerow([
        "States/UTs", "Rice", "Wheat", "Atta (Wheat)", "Gram Dal", "Tur/Arhar Dal", 
        "Urad Dal", "Moong Dal", "Masoor Dal", "Sugar", "Milk @", "Groundnut Oil (Packed)", 
        "Mustard Oil (Packed)", "Vanaspati (Packed)", "Soya Oil (Packed)", "Sunflower Oil (Packed)", 
        "Palm Oil (Packed)", "Gur", "Tea Loose", "Salt Pack (Iodised)", "Potato", "Onion", 
        "Tomato", "Date"
    ])

    while current_date <= end_date:
        data = scrape_data(driver, current_date)
        writer.writerows(data)
        current_date += timedelta(days=1)
        time.sleep(1)

driver.quit()
df = pd.read_csv('combined_retail_price_data.csv')
df.to_csv('combined_retail_price_data.csv', index=False)