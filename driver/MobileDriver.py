import time

from appium import webdriver as mobile
from selenium.common.exceptions import NoSuchElementException


class MobileDriver:

    def __init__(self, parameters):
        self.parameters = parameters
        self.driver = None

    def setup(self):
        if self.parameters['platformName'] == 'Android':
            self.driver = mobile.Remote("http://localhost:4723/wd/hub", self.parameters)
            self.driver.implicitly_wait(10)

        if self.parameters['platformName'] == 'IOS':
            self.driver = None

    def quit(self):
        self.driver.quit()

    # Impact to locator
    def exists(self, locator):
        try:
            return self.driver.find_element(
                locator.by(),
                locator.value()
            ).is_displayed()
        except NoSuchElementException:
            return False

    def not_exists(self, locator):
        try:
            self.driver.find_element(
                locator.by(),
                locator.value()
            )
            return False
        except NoSuchElementException:
            return True

    def click(self, locator):
        self.driver.find_element(
            locator.by(),
            locator.value()
        ).click()

    def clear_field(self, locator):
        self.driver.find_element(
            locator.by(),
            locator.value()
        )(locator).clear()

    def enter_text(self, locator, text):
        self.driver.find_element(
            locator.by(),
            locator.value()
        ).send_keys(text)

    def receive_text(self, locator):
        return self.driver.find_element(
            locator.by(),
            locator.value()
        ).text

    def hide_mobile_keyboard(self):
        self.driver.hide_keyboard()

    def press_back(self):
        self.driver.back()

    def set_location(self, latitude, longitude, altitude):
        print("[set location]: latitude=%s, longitude=%s, altitude=%s" % (latitude, longitude, altitude))
        self.driver.set_location(latitude, longitude, altitude)

    def open_notifications(self):
        self.driver.open_notifications()

    def wait_element(self, locator, wait_time=60):
        now = time.time()
        future = now + wait_time
        while time.time() < future:
            if self.exists(locator):
                return True

        return False

    def battery_info_level(self):
        return self.driver.battery_info["level"]

    # Help
    def page_source(self):
        return self.driver.page_source.encode("utf-8")

    def take_screen_shot(self, path, file_name):
        return self.driver.save_screenshot(path + file_name + '.png')


def check_android_parameters(parameters):
    if parameters["platformName"] is True and parameters["platformName"] == 'Android':
        return False
    # elif parameters["platformVersion"] is True:
    #     return False
    # elif parameters["deviceName"] is True:
    #     return False
    # elif parameters["noReset"] is True:
    #     return False
    # elif parameters["app"] is True:
    #     return False
    # elif parameters["appPackage"] is True:
    #     return False
    # elif parameters["appWaitActivity"] is True:
    #     return False
    else:
        return True


def check_ios_parameters(parameters):
    return False


def check_platform_parameters(parameters):
    if parameters['platformName'] == 'Android':
        return check_android_parameters(parameters)

    if parameters['platformName'] == 'IOS':
        return check_ios_parameters(parameters)

    return False


def driver_factory(parameters):
    if check_platform_parameters(parameters):
        return MobileDriver(parameters)
    else:
        raise Exception('Cannot create Mobile driver. Please check your parameters.')