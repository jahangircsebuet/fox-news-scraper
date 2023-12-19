import logging
import os
from selenium import webdriver
from selenium.webdriver.common.proxy import  Proxy,ProxyType
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
# from python_file.crawler.proxy import ProxyInfo


class Browser:
    logger = logging.getLogger('django.project.requests')
    selenium_retries = 0

    def __init__(self,proxyUse):
        self.proxyUse = proxyUse
        # if self.proxyUse == 1:
        #     self.ProxyPort = ProxyInfo().getProxy()

    def get_option(self):
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems,
                                       limit=100)
        user_agent = user_agent_rotator.get_random_user_agent()

        options = FirefoxOptions()
        # options.add_argument("--headless")
        options.add_argument('--disable—gpu')
        options.add_argument(f'user—agent={user_agent}')
        return options

    def get_proxy(self):
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        firefox_capabilities['proxy'] = {
            "proxyType": "MANUAL",
            "httpProxy": self.ProxyPort,
            "ftpProxy": self.ProxyPort,
            "sslProxy": self.ProxyPort
        }
        return firefox_capabilities


    def getBrowser(self):
        print("getBrowser")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print("dir_path: ", dir_path)

        BROWSER_EXE = '/usr/bin/firefox'
        # GECKODRIVER = dir_path + '/../driver/geckodriver'
        # GECKODRIVER = '/home/super/Downloads/context/geckodriver'
        GECKODRIVER = '/usr/bin/geckodriver'
        print("GECKODRIVER: ", GECKODRIVER)
        FIREFOX_BINARY = FirefoxBinary(BROWSER_EXE)

        PROFILE = webdriver.FirefoxProfile()
        PROFILE.set_preference("dom.webnotifications.enabled", False)
        PROFILE.set_preference("app.update.enabled", False)
        PROFILE.update_preferences()

        options = self.get_option()
        if self.proxyUse == 1:
            capabilities =  self.get_proxy()
            browser = webdriver.Firefox(executable_path=GECKODRIVER, firefox_binary=FIREFOX_BINARY,
                                    firefox_profile=PROFILE,options=options ,desired_capabilities=capabilities)
            return browser
        else:
            browser = webdriver.Firefox(executable_path=GECKODRIVER, firefox_binary=FIREFOX_BINARY,
                                        firefox_profile=PROFILE,
                                        options=options,)
            return browser

if __name__=="__main__":
   browser = Browser(0).getBrowser()
   browser.get("https://www.facebook.com/")