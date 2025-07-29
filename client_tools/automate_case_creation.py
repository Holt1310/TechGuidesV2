"""Simple Selenium script to create a case on the server."""
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options


def create_case(server_url, username, password, template_id, data, driver_path="msedgedriver.exe"):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    service = Service(driver_path)
    driver = webdriver.Edge(service=service, options=options)

    driver.get(f"{server_url}/login")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    driver.get(f"{server_url}/cases/new?template={template_id}")
    time.sleep(1)
    for field, value in data.items():
        elem = driver.find_element(By.NAME, field)
        elem.clear()
        elem.send_keys(str(value))

    driver.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()
    driver.quit()


if __name__ == "__main__":
    server = os.environ.get("TECHGUIDES_URL", "http://localhost:5151")
    user = os.environ.get("TECHGUIDES_USER", "admin")
    pwd = os.environ.get("TECHGUIDES_PASS", "secret")
    template = os.environ.get("CASE_TEMPLATE", "default")
    data_json = os.environ.get("CASE_DATA", "{}")
    data = json.loads(data_json)
    create_case(server, user, pwd, template, data)
