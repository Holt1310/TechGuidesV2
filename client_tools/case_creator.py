#!/usr/bin/env python3
"""Simple Selenium automation to create a case via the web UI."""
import time
import json
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

SERVER_URL = "http://localhost:5151"  # Update if needed
ADMIN_USER = "admin"
ADMIN_PASS = "secret"
TEMPLATE_NAME = "Default"  # name of template to use


def load_template_fields():
    """Fetch template definition via HTTP."""
    import requests
    resp = requests.get(f"{SERVER_URL}/api/case-templates")
    resp.raise_for_status()
    data = resp.json()
    for tpl in data.get("templates", []):
        if tpl["name"] == TEMPLATE_NAME:
            return tpl
    raise RuntimeError("Template not found")


def main():
    tpl = load_template_fields()
    fields = json.loads(tpl["fields_json"])

    service = Service("client_tools/msedgedriver.exe")
    opts = Options()
    driver = webdriver.Edge(service=service, options=opts)

    try:
        driver.get(f"{SERVER_URL}/login")
        driver.find_element(By.NAME, "username").send_keys(ADMIN_USER)
        driver.find_element(By.NAME, "password").send_keys(ADMIN_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        driver.get(f"{SERVER_URL}/cases/new?template={tpl['id']}")
        for f in fields:
            elem = driver.find_element(By.NAME, f['id'])
            if f['type'] == 'select':
                from selenium.webdriver.support.ui import Select
                Select(elem).select_by_index(0)
            else:
                elem.send_keys('test')
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)
    finally:
        driver.quit()


if __name__ == '__main__':
    main()
