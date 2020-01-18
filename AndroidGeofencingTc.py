import time
import subprocess
from enum import Enum
from appium import webdriver as mobile
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By


# html page with results
def get_page_result(data):
    page_start = """<!DOCTYPE html><html><head> <meta charset="utf-8" /> <title>AAS| Tc Results</title> <style> * { background-color: #f3f1f1; } canvas { padding-left: 0; padding-right: 0; margin-left: auto; margin-right: auto; display: block; width: 800px; } #title { text-align: center; } .info { display: grid; grid-template-columns: 80%; justify-content: center; justify-items: center; width: 80%; height: 100%; } .fails { display: none; grid-template-rows: 100%; justify-content: center; justify-items: center; width: 80%; height: 100%; } .info_fails { display: grid; grid-template-columns: 100%; justify-content: center; justify-items: left; width: 80%; height: 100%; } </style></head><body> <h1 id="title"></h1> <div class="wrapper" id="wrapper"> </div> <h2 id="title">Conclusions</h2> <div class="info" id="conclusions"> <h2 id="title">Null</h2> </div> <h2 id="title">Fails</h2> <div class="info" id="fails"> <h2 id="title">Null</h2> </div> <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.min.js"></script> <script> test_name = null; test_time = null; graphs = null; conclusions = null; fails = null; file = """
    page_end = """; function update_data() { test_name = file.test_name; test_time = file.test_time; graphs = file.graphs; conclusions = file.conclusions; fails = file.fails; document.title = test_name }; function create_notifications(id, title, labels, label, data, color = "#00FF00", mfill = true, yTitle = 'Seconds', xTitle = 'Iteration', beginAtZero = true) { new Chart(document.getElementById(id), { type: 'line', data: { labels: labels, datasets: [{ data: data, label: label, borderColor: '#DF0101', backgroundColor: color, fill: mfill }] }, options: { title: { display: true, text: title }, scales: { yAxes: [{ ticks: { beginAtZero: beginAtZero }, scaleLabel: { display: true, labelString: yTitle } }], xAxes: [{ ticks: { beginAtZero: beginAtZero }, scaleLabel: { display: true, labelString: xTitle } }] } } }) } function create_graphs() { document.getElementById('title').innerHTML = test_name + ", time: " + test_time + " (in hours)"; str = ""; for (i = 0; i < graphs.length; i++) { str += "<div class=\\\"info\\\"><canvas id=\\\"" + graphs[i].id_graph + "\\\"></canvas></div>" }; document.getElementById('wrapper').innerHTML = str }; function update_conclusions() { document.getElementById("conclusions").innerHTML = conclusions }; function open_screenshot(id) { if (id.style.display == "grid") { id.style.display = "none" } else { id.style.display = "grid" } }; function update_fails() { str = ""; for (i = 0; i < fails.length; i++) { str += "<div class=\\\"info_fails\\\"> <b onclick=\\\"open_screenshot(img_" + i + ")\\\" >" + i + ") " + fails[i].action + "</b>" + "<img id=\\\"img_\" + i + "\\\" class=\\\"fails\\\" src=\\\"" + fails[i].img_path + "\\\" /></div>" } document.getElementById("fails").innerHTML = str } function update_graphs() { for (i = 0; i < graphs.length; i++) { for (j = 0; j < graphs[i].y_data.length; j++) { if (graphs[i].y_data[j] <= 0) { graphs[i].y_data[j] = null } } } for (i = 0; i < graphs.length; i++) { create_notifications( graphs[i].id_graph, graphs[i].title, graphs[i].x_data, graphs[i].label, graphs[i].y_data, graphs[i].border_color, mfill = true, graphs[i].y_title, graphs[i].x_title, graphs[i].begin_at_zero ) } } function update() { update_graphs(); update_conclusions(); update_fails(); } update_data(); create_graphs(); update(); function update_page() {document.location.reload(true)}; setInterval(update_page, 30 * 1000) </script></body></html>"""
    return page_start + data + page_end


class StartLocation:
    def __init__(self, latitude: float, longitude: float, altitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude


class ObjectToMove(Enum):
    PEDESTRIAN = "Pedestrian"
    CAR = "Car"
    TELEPORT = "Teleport"


class ObjectCapabilities:
    def __init__(self, object_to_move: ObjectToMove):
        if object_to_move == ObjectToMove.PEDESTRIAN:
            self.step = 0.0000100
            self.times = 100
            self.pause = 1

        if object_to_move == ObjectToMove.CAR:
            self.step = 0.0001000
            self.times = 40
            self.pause = 1

        if object_to_move == ObjectToMove.TELEPORT:
            self.step = 0.0100000
            self.times = 1
            self.pause = 2


class Locator:

    def __init__(self, by, value, description, dynamic_value=None):
        self._by = by
        self._value = value
        self._description = description
        self.dynamic_value = dynamic_value

    def value(self):
        return self._value if self.dynamic_value is None else self._value % self.dynamic_value

    def by(self):
        return self._by

    def description(self):
        return self._description


def create_locator(by, value, description, dynamic_value=None):
    return Locator(
        by,
        value,
        description,
        dynamic_value
    )


# Locators
login_btn = create_locator(By.XPATH, "//*[contains(@text, 'LOG')]", "Login Button")
email_field = create_locator(By.XPATH, "//android.widget.EditText[contains(@resource-id, 'email')]", "Email Field")
password_field = create_locator(By.XPATH, "//android.widget.EditText[contains(@resource-id, 'password')]", "Pass Field")
ok_btn = create_locator(By.XPATH, "//*[contains(@text, 'OK')]", "Ok Button")
allow_btn = create_locator(By.XPATH, "//*[contains(@text, 'ALLOW')]", "ALLOW Button")
clear_btn = create_locator(By.XPATH,
                           "//*[@id='com.android.systemui:id/dismiss_text' or contains(@text, 'Clear') or contains("
                           "@text, 'CLEAR')]",
                           "Clear Button")


class MobileDriver:

    def __init__(self, parameters):
        self.parameters = parameters
        self.driver = None

    def setup(self):
        print("Setup MobileDriver")
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
    elif parameters["platformVersion"] is True:
        return False
    elif parameters["deviceName"] is True:
        return False
    elif parameters["noReset"] is True:
        return False
    elif parameters["app"] is True:
        return False
    elif parameters["appPackage"] is True:
        return False
    elif parameters["appWaitActivity"] is True:
        return False
    else:
        return True


def check_platform_parameters(parameters):
    if parameters['platformName'] == 'Android':
        return check_android_parameters(parameters)

    return False


def driver_factory(parameters):
    if check_platform_parameters(parameters):
        return MobileDriver(parameters)
    else:
        raise Exception('Cannot create Mobile driver. Please check your parameters.')


class Graph:

    def __init__(self, id_graph: str, title: str, label: str, begin_at_zero: bool, border_color: str, x_title: str,
                 y_title: str):
        self.id_graph = id_graph
        self.title = title
        self.label = label
        self.begin_at_zero = begin_at_zero
        self.border_color = border_color
        self.x_data = []
        self.x_title = x_title
        self.y_data = []
        self.y_title = y_title

    def add_data(self, x, y):
        self.x_data.append(x)
        self.y_data.append(y)

    def __str__(self):
        return "\"id_graph\": {}, \"title\": {}, \"label\": {}, \"begin_at_zero\": {}, \"border_color\": {}, " \
               "\"x_data\": {}, \"x_title\": {}, \"y_data\": {}, \"y_title\": {}" \
            .format(self.id_graph, self.title, self.label, self.begin_at_zero, self.border_color, self.x_data,
                    self.x_title, self.y_data, self.y_title)


class Fails:
    def __init__(self, action: str, img_path: str):
        self.action = action
        self.img_path = img_path


class Report:
    def __init__(self, test_name: str, test_time: float):
        self.test_name = test_name
        self.test_time = test_time
        self.graphs = []
        self.fails = []
        self.conclusions = ""

    def add_graph(self, id_graph: str, title: str, label: str, begin_at_zero: bool, border_color: str, x_title: str,
                  y_title: str):
        self.graphs.append(Graph(id_graph, title, label, begin_at_zero, border_color, x_title, y_title))

    def get_graph(self, id_graph: str):
        for graph in self.graphs:
            if graph.id_graph == id_graph:
                return graph
        return None

    def add_fails(self, action: str, img_path: str):
        self.fails.append(
            Fails(action, img_path)
        )

    def __str__(self):
        global path
        json_str = "{\n"
        json_str += "\t\"test_name\": \"%s\", \n" % self.test_name
        json_str += "\t\"test_time\": \"%s\", \n" % self.test_time
        json_str += "\t\"conclusions\": \"%s\", \n" % self.conclusions
        json_str += "\t\"graphs\": [\n"
        size = len(self.graphs)
        for graph in self.graphs:
            json_str += "\t{ \n"
            json_str += "\t\t\"id_graph\": \"%s\", \n" % graph.id_graph
            json_str += "\t\t\"title\": \"%s\", \n" % graph.title
            json_str += "\t\t\"label\": \"%s\", \n" % graph.label
            json_str += "\t\t\"begin_at_zero\": \"%s\", \n" % graph.begin_at_zero
            json_str += "\t\t\"border_color\": \"%s\", \n" % graph.border_color
            json_str += "\t\t\"x_data\": %s, \n" % graph.x_data
            json_str += "\t\t\"x_title\": \"%s\", \n" % graph.x_title
            json_str += "\t\t\"y_data\": %s, \n" % graph.y_data
            json_str += "\t\t\"y_title\": \"%s\"\n" % graph.y_title
            size -= 1
            if size <= 0:
                json_str += "\t }"
            else:
                json_str += "\t },\n"
        json_str += "],\n"

        json_str += "\t\"fails\": [\n"
        size = len(self.fails)
        for fail in self.fails:
            json_str += "\t{ \n"
            json_str += "\t\t\"action\": \"%s\", \n" % fail.action
            json_str += "\t\t\"img_path\": \"{}{}\" \n".format(path, fail.img_path)
            size -= 1
            if size <= 0:
                json_str += "\t }"
            else:
                json_str += "\t },\n"
        json_str += "]\n"
        json_str += "}"
        return json_str


def check_notification(driver: MobileDriver, text: str, report: Report, iteration):
    global clear_btn, path
    driver.open_notifications()

    notification = create_locator(By.XPATH, "//*[contains(@text, '%s')]" % text, text)
    start = time.time()
    notification_time = -100
    if driver.wait_element(notification):
        notification_time = int(time.time() - start)
    else:
        img = str(int(start))
        if driver.take_screen_shot(path, img):
            report.add_fails(
                "Iteration №" + str(iteration) + " - " + text + "? - " + str(False),
                img + ".png"
            )

    # close notification
    if driver.exists(clear_btn):
        driver.click(clear_btn)
        time.sleep(2)

    if driver.exists(clear_btn):
        driver.press_back()

    return notification_time


def geofencing(driver: MobileDriver, mover: ObjectCapabilities, start_location: StartLocation, report: Report):
    global path
    iteration = 0
    start_tc_time = time.time()
    stop_tc_time = start_tc_time + (report.test_time * 60 * 60)

    driver.set_location(start_location.latitude, start_location.longitude, start_location.altitude)
    logcat_command = 'adb logcat > {}logcat.txt'.format(path)
    logcat_procces = subprocess.Popen([logcat_command], shell=True)
    while time.time() < stop_tc_time:
        print("========= Iteration number %s =========" % iteration)
        # navigate away
        counter = 0
        time.sleep(mover.pause)
        while counter < mover.times:
            start_location.latitude += mover.step
            start_location.longitude += mover.step
            driver.set_location(start_location.latitude, start_location.longitude, start_location.altitude)
            counter += 1

        notification_time = check_notification(driver, "is now Away mode", report, iteration)
        report.get_graph("away_notification").add_data(
            iteration,
            notification_time
        )
        print("Away Mode: %s secs" % notification_time)

        # navigate home
        counter = 0
        time.sleep(mover.pause)
        while counter < mover.times:
            start_location.latitude -= mover.step
            start_location.longitude -= mover.step
            driver.set_location(start_location.latitude, start_location.longitude, start_location.altitude)
            counter += 1

        notification_time = check_notification(driver, "is now Home mode", report, iteration)
        report.get_graph("home_notification").add_data(
            iteration,
            notification_time
        )
        print("Home Mode: %s secs" % notification_time)

        battery = driver.battery_info_level() * 100
        print("Battery level: %s" % battery)
        report.get_graph("battery_consumption").add_data(
            int(time.time() - start_tc_time),
            battery
        )

        print("Iteration time: %s secs" % int(time.time() - start_tc_time))
        print("Tc time: %s secs" % int(stop_tc_time))
        print("Remaining time: %s secs" % int(stop_tc_time - time.time() + start_tc_time))

        update_conclusions(report)
        iteration += 1
        print("Update report.json")
        f = open("{}report.json".format(path), "w")
        f.write(report.__str__())
        f.close()
        print("Update page.html")
        f2 = open("{}page.html".format(path), "w")
        f2.write(get_page_result(report.__str__()))
        f2.close()

    logcat_procces.terminate()


def update_conclusions(report: Report):
    home_notification = [element for element in report.get_graph("home_notification").y_data if element >= 0]
    away_notification = [element for element in report.get_graph("away_notification").y_data if element >= 0]
    battery_consumption = [element for element in report.get_graph("battery_consumption").y_data if element >= 0]

    if len(home_notification) <= 0 or len(away_notification) <= 0:
        return

    conclusions_home_notification = "Home Mode: Max={}, Min={}, Average={} (in seconds)." \
        .format(max(home_notification), min(home_notification), sum(home_notification) / len(home_notification))
    conclusions_away_notification = "Away Mode: Max={}, Min={}, Average={} (in seconds)." \
        .format(max(away_notification), min(away_notification), sum(away_notification) / len(home_notification))
    conclusions_battery_consumption = "Battery Level: Start={}, Now={}, Change={} (in percents)." \
        .format(battery_consumption[0], battery_consumption[-1], battery_consumption[0] - battery_consumption[-1])

    report.conclusions = "{} {} {}".format(conclusions_home_notification, conclusions_away_notification,
                                           conclusions_battery_consumption)


def run_geofencing_tc(driver: MobileDriver, object_to_move: ObjectToMove, start_location: StartLocation,
                      report: Report, device: str):
    mover = ObjectCapabilities(object_to_move)

    report.add_graph(
        id_graph="home_notification",
        title="Home Mode Notifications",
        label="Notifications time (in seconds)",
        begin_at_zero=True,
        border_color="#6bc52b",
        x_title="Iterations",
        y_title="Seconds"
    )

    report.add_graph(
        id_graph="away_notification",
        title="Away Mode Notifications",
        label="Notifications time (in seconds)",
        begin_at_zero=True,
        border_color="#e8e234",
        x_title="Iterations",
        y_title="Seconds"
    )

    report.add_graph(
        id_graph="battery_consumption",
        title="Battery consumption",
        label="Device: {}".format(device),
        begin_at_zero=False,
        border_color="#b18a8a",
        x_title="Time (in seconds)",
        y_title="Battery Level (in percent)"
    )

    geofencing(driver, mover, start_location, report)


def login():
    global driver, account_email, account_password
    print("Login")
    driver.click(login_btn)
    driver.enter_text(email_field, account_email)
    driver.hide_mobile_keyboard()
    driver.enter_text(password_field, account_password)
    driver.hide_mobile_keyboard()
    driver.click(login_btn)
    time.sleep(20)


def approve_geofencing_mode():
    global driver
    print("Approve Geofencing Mode")
    driver.click(ok_btn)
    driver.click(allow_btn)
    time.sleep(20)


#############################################################################
#############################################################################
#############################################################################
# Device & Application capabilities
capabilities = {
    "platformName": "Android",
    "platformVersion": "8.1.0",
    "deviceName": "6803a8f07d26",
    "app": "*****",
    "appWaitActivity": "*",
    "noReset": False,
    "appPackage": "*****"
}
# Folder to save results
path = "/root/Downloads/tc_results/"
# Test time (in hours)
tc_time = 1
# Account
account_email = "cqa.automation.gen5.egor.exisiting+06@gmail.com"
account_password = "Mm328328"
# Start location
latitude: float = 53.894015
longitude: float = 27.561444
altitude: float = 20
# PEDESTRIAN, CAR or TELEPORT Modes
mover = ObjectToMove.TELEPORT
#############################################################################
#############################################################################
#############################################################################
# Report
report = Report("Android Geofencing Tc", tc_time)

# Test logic
driver = driver_factory(capabilities)
start_location: StartLocation = StartLocation(latitude, longitude, altitude)
driver.setup()
login()
approve_geofencing_mode()
run_geofencing_tc(driver, mover, start_location, report, capabilities["deviceName"])
