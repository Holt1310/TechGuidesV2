"""Simple Selenium automation for creating a case."""
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import json
import os

SERVER_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = os.environ.get("TRUCKSOFT_ADMIN_PASSWORD", "secret")

TEMPLATE_NAME = "Default"

def main():
    service = Service(os.path.join(os.path.dirname(__file__), "msedgedriver.exe"))
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Edge(service=service, options=options)

    driver.get(f"{SERVER_URL}/login")
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    time.sleep(1)

    driver.get(f"{SERVER_URL}/cases/new")
    select = driver.find_element(By.NAME, "template_id")
    for option in select.find_elements(By.TAG_NAME, "option"):
        if option.text.strip() == TEMPLATE_NAME:
            option.click()
            break
    driver.find_element(By.CSS_SELECTOR, "button.btn-primary").click()
    time.sleep(1)

    # Fill fields with dummy data
    inputs = driver.find_elements(By.CSS_SELECTOR, "#caseForm input")
    for inp in inputs:
        inp.clear()
        inp.send_keys("test")

    driver.find_element(By.CSS_SELECTOR, "#caseForm button").click()
    time.sleep(1)
    driver.quit()
    print("Case submitted")

if __name__ == "__main__":
    main()
