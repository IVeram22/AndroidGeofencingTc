from selenium.webdriver.common.by import By
from helper.Helper import *
from driver import MobileDriver
from driver.MobileDriver import driver_factory
from locator.Locator import create_locator
from report.Report import Report
from tests.Geofencing import StartLocation, ObjectToMove, geofencing, run_geofencing_tc

capabilities = {
    "platformName": "Android",
    "platformVersion": "8.0",
    "deviceName": "ce0117115be70d2305",
    "app": "/root/Downloads/hmsandroid.apk",
    "appWaitActivity": "*",
    "noReset": False,
    "appPackage": "com.arlo.qa2"
}

driver: MobileDriver = driver_factory(capabilities)

driver.setup()

login_btn = create_locator(By.XPATH, "//*[contains(@text, 'LOG')]", "Login Button")
email_field = create_locator(By.XPATH, "//android.widget.EditText[contains(@resource-id, '%s')]", "Email Field",
                             "email")
password_field = create_locator(By.XPATH, "//android.widget.EditText[contains(@resource-id, '%s')]", "Password Field",
                                "password")

driver.click(login_btn)
driver.enter_text(email_field, "cqa.automation.gen5.egor.exisiting+06@gmail.com")
driver.hide_mobile_keyboard()
driver.enter_text(password_field, "Mm328328")
driver.hide_mobile_keyboard()
driver.click(login_btn)
sleep(20)

ok_btn = create_locator(By.XPATH, "//*[contains(@text, 'OK')]", "Ok Button")
allow_btn = create_locator(By.XPATH, "//*[contains(@text, 'ALLOW')]", "ALLOW Button")

driver.click(ok_btn)
driver.click(allow_btn)

sleep(20)

start_location: StartLocation = StartLocation(53.894015, 27.561444, 20)
mover = ObjectToMove.TELEPORT

report = Report("Android Geofencing Tc", 1)
run_geofencing_tc(driver, mover, start_location, report, capabilities.deviceName)
