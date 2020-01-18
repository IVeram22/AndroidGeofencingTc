from appium import webdriver as mobile
from selenium.webdriver.common.by import By

driver = None
capabilities = {
    "platformName": "Android",
    "deviceName": "ce0117115be70d2305",
    "app": "/root/Downloads/hmsandroid.apk",
    "appWaitActivity": "*"

}


def init_driver():
    global driver, capabilities
    if driver is None:
        driver = mobile.Remote("http://localhost:4723/wd/hub", capabilities)
        driver.implicitly_wait(10)
        print(driver.battery_info)


def login(email, password):
    global driver
    driver.find_element_by_xpath("//*[contains(@text, 'LOG')]").click()
    driver.implicitly_wait(10)
    driver.find_element_by_xpath("//android.widget.EditText[contains(@resource-id, 'email')]").send_keys(email)
    driver.hide_keyboard()
    driver.find_element_by_xpath("//android.widget.EditText[contains(@resource-id, 'password')]").send_keys(password)
    driver.hide_keyboard()
    driver.find_element_by_xpath("//*[contains(@text, 'LOG')]").click()


def open_notifications():
    global driver
    driver.open_notifications()

# driver.find_element_by_xpath("//*[contains(@text, 'LOG')]").click()
# driver.back()

# driver.set_location(53.8989777, 27.5682829, 18.5)

init_driver()
# login("cqa.automation.gen5.egor.exisiting+06@gmail.com", "Mm328328")
open_notifications()

a = driver.find_element_by_xpath("//*[@id='com.android.systemui:id/dismiss_text' or contains(@text, 'Clear') or contains(@text, 'CLEAR')]")
#
# a.click()

print("Done.")

import os
myCmd = 'adb logcat > 1.txt'
a = os.system(myCmd)
