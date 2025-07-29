#!/usr/bin/env python3
"""Simple Selenium automation script to create a case."""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'case_creator_config.json')


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "url": "http://localhost:5151",
        "username": "admin",
        "password": "secret",
        "template_id": 1,
        "fields": {}
    }


def main():
    config = load_config()
    driver_path = os.path.join(os.path.dirname(__file__), 'msedgedriver.exe')
    options = Options()
    options.add_argument('--headless')
    service = Service(driver_path)
    driver = webdriver.Edge(service=service, options=options)

    try:
        driver.get(f"{config['url']}/login")
        driver.find_element(By.NAME, 'username').send_keys(config['username'])
        driver.find_element(By.NAME, 'password').send_keys(config['password'])
        driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
        time.sleep(1)

        driver.get(f"{config['url']}/cases/new?template_id={config['template_id']}")
        for field_id, value in config.get('fields', {}).items():
            elem = driver.find_element(By.NAME, field_id)
            elem.clear()
            elem.send_keys(value)
        driver.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()
        time.sleep(1)
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
