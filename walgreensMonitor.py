from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import configparser
import threading
import time
import datetime
import os
import winsound
import enumeratedVariables as Constants

class Monitor:

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.getcwd(), 'config.ini'))
        self.driver = webdriver.Chrome(executable_path=os.path.join(os.getcwd(), 'chromedriver.exe'))
        self.incomming_message_sound = 'Sound_clips/incoming_message.wav'
        self.sound_clip_directory = os.path.join(os.getcwd(), "Sound_clips")
        self.errors = 0
        self.alarmActive = False
        # CONFIG VARIABLES###############################################################################################################################################################################
        #email address for Walgreens ex: John-appleseed@apple.com
        self.email = self.config['account']['email']
        print(self.email)

        #password for Walgreens ex: PaSsWoRd1@3$
        self.password = self.config['account']['password']
        print(self.password)

        # Are you a healthcare worker, older than 65, essential worker, or have an underlying condition? Copy and paste the text between the "" and paste between the "" next to self.eligibility.
        # Healthcare workers = "HEALTHCARE_WORKER"
        # Older than 65 = "OLDER_THAN_65"
        # Essential workers = "ESSENTIAL_WORKER"
        # Underlying conditions = "UNDERLYING_CONDITION"
        try:
            self.eligibility = Constants.Eligibility[self.config['info']['eligibility'].upper()].value
            print(self.eligibility)
        except KeyError:
            self.errors += 1
            print("Eligibility input in config.ini is not compatible")

        #zip codes to check. Make sure they are all in the same state, separated by commas, and no spaces! ex: "90210,91331,90650" will check 90210 91331 and 90650
        self.zip = self.config['info']['zipcode']
        self.zip = self.zip.replace(" ", "").split(",")

        # Copy and paste one of the following strings between the "" next to self.race
        # Native American = "Native American"
        # Asian = "Asian"
        # Black = "Black"
        # Native Hawaiian = "Native Hawaiian"
        # White = "White"
        # Other = "Other"
        self.races = {"NATIVE AMERICAN" : "1002-5", "ASIAN" : "2028-9", "BLACK" : "2054-5", "NATIVE HAWAIIAN" : "2076-8", "WHITE" : "2106-3", "OTHER" : "2131-1"}
        try:
            self.race = self.races[self.config['info']['race'].upper()]
            print(self.race)
        except KeyError:
            self.errors += 1
            print("Race input in config.ini is not compatible")
        
        # Copy and paste one of the following strings between the "" next to self.ethnicity
        # Hispanic or Latino = "Hispanic"
        # Non-Hispanic = "NonHispanic"
        # Unknown = "Unknown"
        # Decline to answer = "Decline"
        self.ethnicities = {"HISPANIC" : "2186-5", "NONHISPANIC" : "2186-5", "UNKNOWN" : "UNK", "DECLINE": "POL"}
        try:
            self.ethnicity = self.ethnicities[self.config['info']['ethnicity'].upper()]
            print(self.ethnicity)
        except KeyError:
            self.errors += 1
            print("Ethnicity input in config.ini is not compatible")

        # Copy and paste one of the following strings between the "" next to self.doseNumber
        # Scheduling first and second dose = "FIRST_AND_SECOND_DOSE"
        # Scheduling second dose only = "SECOND_DOSE"
        try:
            self.doseNumber = Constants.Dose[self.config['info']['dose'].upper()].value
            print(self.doseNumber)
        except KeyError:
            self.errors += 1
            print("Dose input in config.ini is not compatible")

        try:
            self.appointmentTime = Constants.AppointmentTime[self.config['info']['appointmentTime'].upper()].value
            print(self.appointmentTime)
        except:
            self.errors += 1
            print("Appointment Time in config.ini is not compatible")
            
        # Check for errors to let the user know they need to fix their configuration
        if self.errors > 0:
            raise KeyError()
        # END CONFIG VARIABLES###############################################################################################################################################################################
        
        

        self.unavailableMessage = "We don't have any available appointments coming up within"

    def alarm(self):
        if not self.alarmActive:
            self.alarmActive = True
            while(True):
                winsound.PlaySound(self.incomming_message_sound, winsound.SND_NOSTOP)

    def radioInput(self):
        print("Selecting radio buttons")
        radioButtons = self.driver.find_elements_by_xpath("//div[@class='sv_q_radiogroup undefined sv-q-col-1']")
        radioButtons[1].click()
        time.sleep(0.5)
        radioButtons[3].click()
        time.sleep(0.5)
        radioButtons[5].click()
        time.sleep(0.5)
        radioButtons[6].click()
        time.sleep(0.5)
        #next button
        self.driver.find_element_by_class_name("sv_complete_btn").click()
        time.sleep(4)
        self.driver.find_element_by_class_name("button-agree").click()
        time.sleep(4)

    def miscInput(self):
        print("Selecting misc input")
        #race selection
        race = self.driver.find_element_by_id("race-dropdown")
        race.find_element_by_xpath("//option[@value='{}']".format(self.race)).click()
        time.sleep(0.5)
        #ethnicity selection
        ethnicity = self.driver.find_element_by_id("ethnicity-dropdown")
        ethnicity.find_element_by_xpath("//option[@value='{}']".format(self.ethnicity)).click()
        #Shot selection
        radioButtons = self.driver.find_elements_by_xpath("//div[@class='btn__radio']")
        radioButtons[self.doseNumber].click()
        time.sleep(0.5)
        #next button
        self.driver.find_element_by_class_name("btn__pair").click()
        time.sleep(5)

    def login(self):
        print("Logging into: {}".format(self.email))
        self.driver.get('https://www.walgreens.com/login.jsp')
        time.sleep(2)
        emailTextField = self.driver.find_element_by_id('user_name')
        emailTextField.click()
        emailTextField.send_keys(self.email)
        time.sleep(0.5)
        passwordTextField = self.driver.find_element_by_id('user_password')
        passwordTextField.click()
        passwordTextField.send_keys(self.password)
        self.driver.find_element_by_id('submit_btn').click()
        time.sleep(7)

    def preSurveyZip(self):
        print("Pre-Survey Zipcode")
        while(True):
            e = datetime.datetime.now()
            print ("The time is now: = %s:%s:%s" % (e.hour, e.minute, e.second))
            self.driver.get('https://www.walgreens.com/findcare/vaccination/covid-19/location-screening')
            time.sleep(4)
            locationInput = self.driver.find_element_by_id("inputLocation")
            for i in range(3):
                for zipCode in self.zip:
                    locationInput.click()
                    locationInput.clear()
                    locationInput.send_keys(zipCode)
                    time.sleep(3)
                    self.driver.find_element_by_class_name("btn").click()
                    time.sleep(5)
                    try:
                        popUp = self.driver.find_element_by_class_name("fs16")
                        print(popUp.text + " in: {}".format(zipCode))
                        if popUp.text != "Appointments unavailable":
                            self.driver.find_element_by_class_name("mt15").click()
                            time.sleep(4)
                            return
                            #self.agreementCheckbox()
                            #self.radioInput()
                            #self.miscInput()
                            #self.scheduleTime()
                    except:
                        pass
                    time.sleep(1)

    def agreementCheckbox(self):
        print("Agreement Checkbox")
        self.driver.find_elements_by_xpath("//div[@class='sv_q_radiogroup undefined sv-q-col-1']")[self.eligibility].click()
        time.sleep(1)
        self.driver.find_element_by_id("eligibility-check").click()
        time.sleep(1)
        self.driver.find_element_by_class_name("sv_complete_btn").click()
        time.sleep(5)

    def scheduleTime(self):
        timeSlot = self.driver.find_elements_by_class_name("content")
        timeSlot[self.appointmentTime].click()
        threading.Thread(target=self.alarm, daemon=True).start()
        while(True):
            time.sleep(1)
        print("Selecting first time slot")
        time.sleep(2)
        self.driver.find_element_by_xpath("//button[@class ='confirmDoseTimeslots btn btn__blue btn__full-width ']").click()
        print("Selecting second time slot")
        timeSlot = self.driver.find_elements_by_class_name("content")
        timeSlot[self.appointmentTime].click()
        while(True):
            time.sleep(1)
        

    def checker(self):
        time.sleep(0.5)
        while(True):
            try:
                e = datetime.datetime.now()
                print ("The time is now: = %s:%s:%s" % (e.hour, e.minute, e.second))
                #login page
                self.login()
                while(True):
                    try:
                        self.preSurveyZip()
                        self.agreementCheckbox()
                        self.radioInput()
                        self.miscInput()
                        self.scheduleTime()
                    except Exception as e:
                        print(e)
                        self.errors += 1
                        print("Errors: " + str(self.errors))
                    time.sleep(5)
                
            except Exception as e:
                print(e)
                self.errors += 1
                print("Errors: " + str(self.errors))
            time.sleep(5)
try:
    checker = Monitor()
    checker.checker()
except Exception as e:
    print(e)