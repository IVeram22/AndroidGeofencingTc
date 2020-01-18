import json
import os
import pickle
import subprocess
from enum import Enum

import serializers as serializers
from selenium.webdriver.common.by import By

from driver import MobileDriver
from helper.Helper import *
from locator.Locator import create_locator
from report.Report import Report

clear_btn = create_locator(By.XPATH,
                           "//*[@id='com.android.systemui:id/dismiss_text' or contains(@text, 'Clear') or contains("
                           "@text, 'CLEAR')]",
                           "Clear Button")


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
            self.step = 0.0000100
            self.times = 100
            self.pause = 1

        if object_to_move == ObjectToMove.TELEPORT:
            self.step = 0.0100000
            self.times = 1
            self.pause = 2


def check_notification(driver: MobileDriver, text: str, report: Report, iteration):
    global clear_btn
    driver.open_notifications()

    notification = create_locator(By.XPATH, "//*[contains(@text, '%s')]" % text, text)
    start = time.time()
    notification_time = -100
    if driver.wait_element(notification):
        notification_time = int(time.time() - start)
    else:
        img = str(int(start))
        if driver.take_screen_shot("", img):
            report.add_fails(
                "Iteration №"+str(iteration)+" - "+text + "? - " + str(False),
                img + ".png"
            )

    # close notification
    if driver.exists(clear_btn):
        driver.click(clear_btn)
        sleep(2)

    if driver.exists(clear_btn):
        driver.press_back()

    return notification_time


def geofencing(driver: MobileDriver, mover: ObjectCapabilities, start_location: StartLocation, report: Report):
    iteration = 0
    start_tc_time = time.time()
    stop_tc_time = start_tc_time + (report.test_time * 60 * 60)

    driver.set_location(start_location.latitude, start_location.longitude, start_location.altitude)
    myCmd = 'adb logcat > logcat.txt'
    logcat = subprocess.Popen([myCmd], shell=True)
    while time.time() < stop_tc_time:
        print("========= Iteration number %s =========" % iteration)
        # navigate away
        counter = 0
        sleep(mover.pause)
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
        sleep(mover.pause)
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
        f = open("report.json", "w")
        f.write(report.__str__())
        f.close()

    logcat.terminate()


def update_conclusions(report: Report):
    home_notification = [element for element in report.get_graph("home_notification").y_data if element >= 0]
    away_notification = [element for element in report.get_graph("away_notification").y_data if element >= 0]
    battery_consumption = [element for element in report.get_graph("battery_consumption").y_data if element >= 0]

    conclusions_home_notification = "Home Mode: Max={}, Min={}, Average={} (in seconds)." \
        .format(
        max(home_notification),
        min(home_notification),
        sum(home_notification) / len(home_notification)
    )
    conclusions_away_notification = "Away Mode: Max={}, Min={}, Average={} (in seconds)." \
        .format(
        max(away_notification),
        min(away_notification),
        sum(away_notification) / len(home_notification)
    )
    conclusions_battery_consumption = "Battery Level: Start={}, Now={}, Change={} (in percents)." \
        .format(
        battery_consumption[0],
        battery_consumption[-1],
        battery_consumption[0] - battery_consumption[-1]
    )

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
