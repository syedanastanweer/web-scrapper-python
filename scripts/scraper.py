import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re

def scrap_data(url):
    # Configure WebDriver (headless mode for scraping)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Fetch URL
    driver.get(url)
    time.sleep(3)  # Allow the page to load

    # Data placeholders for storing individual data categories
    data = []
    email_column = []
    phone_column = []
    name_column = []
    other_details_column = []

    # Regex Patterns to detect Email and Phone Numbers
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"(\+?\d{1,3}[\s-]?)?(\(?\d{1,4}\)?[\s-]?)?[\d\s-]{5,}"

    try:
        # Extract emails, phones, and paragraphs
        emails = [e.text for e in driver.find_elements(By.XPATH, "//a[contains(@href, 'mailto:')]")]
        phones = [p.text for p in driver.find_elements(By.XPATH, "//a[contains(@href, 'tel:')]")]
        paragraphs = [p.text for p in driver.find_elements(By.TAG_NAME, "p")]
        
        # Add the emails to the email_column
        for email in emails:
            if re.match(email_pattern, email):
                email_column.append(email)
            else:
                email_column.append("Invalid Email")

        # Add the phone numbers to the phone_column
        for phone in phones:
            if re.match(phone_pattern, phone):
                phone_column.append(phone)
            else:
                phone_column.append("Invalid Phone")

        # Detect name: Here we look for headings or bold tags; adjust as needed based on page structure
        names = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //strong")  # Searching common tags
        for name in names:
            if name.text.strip() != "":  # Avoid adding empty entries
                name_column.append(name.text.strip())
        
        # Handle "Other Details" as text paragraphs and anything else not email/phone/name
        for para in paragraphs:
            if re.match(email_pattern, para):
                email_column.append(para)  # Add email-like paragraphs under the Email column
            elif re.match(phone_pattern, para):
                phone_column.append(para)  # Add phone-like paragraphs under the Phone column
            else:
                other_details_column.append(para.strip())

        # Prepare the columns: Ensure they all match lengths (padded if necessary)
        max_len = max(len(email_column), len(phone_column), len(name_column), len(other_details_column))
        
        while len(email_column) < max_len:
            email_column.append("Not Found")
        while len(phone_column) < max_len:
            phone_column.append("Not Found")
        while len(name_column) < max_len:
            name_column.append("Not Found")
        while len(other_details_column) < max_len:
            other_details_column.append("Not Found")

        # Prepare data as rows in columns
        for i in range(max_len):
            row = {
                "Email": email_column[i],
                "Phone": phone_column[i],
                "Name": name_column[i],
                "Other Details": other_details_column[i]
            }
            data.append(row)

    except Exception as e:
        print(f"Error during scraping: {e}")

    # Save Data to CSV and XLSX files
    output_dir = "static/files"
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame(data)  # Creating a DataFrame with dynamic column names
    df.to_csv(f"{output_dir}/output_data.csv", index=False)
    df.to_excel(f"{output_dir}/output_data.xlsx", index=False)

    driver.quit()

    return "Scraping complete!", len(data)

