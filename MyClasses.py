# Import packages
import sys
import os
import logging
import configparser
import ctypes

class AppGeneral:
    def __init__(self, project_name, pLogger, log_string):
        self.project_name = project_name
        self.logger = pLogger
        self.log_string = log_string
    
    def initialise_app(self):
        pass
    
    def finalise_app(self, is_app_end):
        complete_message = "App complete running successfully"
        self.logger.info(complete_message + self.log_string)
        if is_app_end:
            ctypes.windll.user32.MessageBoxW(0, complete_message, self.project_name, 0) # Last 0 for OK
        else:
            sys.exit()
    
    def parse_boolean_string(self, pString):
        if pString == "True":
            return True
        return False

class MyLogger:
    def __init__(self, project_name):
        self.project_name = project_name
        self.my_logger = self.create_logger()
    
    def create_logger(self):
        my_logger = logging.getLogger("my_logger")
        my_logger.setLevel(logging.INFO)
        my_log_formatter = logging.Formatter("[%(asctime)s] %(message)s")
        my_stream_handler = logging.StreamHandler(sys.stdout)
        my_stream_handler.setFormatter(my_log_formatter)
        my_logger.addHandler(my_stream_handler)
        my_file_handler = logging.FileHandler("app_data\\" + self.project_name + ".log")
        my_file_handler.setFormatter(my_log_formatter)
        my_logger.addHandler(my_file_handler)
        return my_logger

class MyConfig:
    def __init__(self, project_name, pLogger):
        self.project_name = project_name
        self.logger = pLogger
        self.my_config = configparser.ConfigParser()
    
    def create_file_specific(self):
        self.my_config["Heading1"] = {}
        self.my_config["Heading1"]["switch1"] = "False"
        self.my_config["Heading1"]["var1"] = "String"

    def create_file(self):
        self.my_config["App"] = {}
        self.my_config["App"]["log_level"] = "INFO"

        with open("config.ini", 'w') as config_file:
            self.my_config.write(config_file)
        self.logger.info("Config file written to %s", os.getcwd() + "\\" + "config.ini")
        return ctypes.windll.user32.MessageBoxW(0, "Config file written\n\nOK to continue, Cancel to exit", self.project_name, 1) # 1 for OK and Cancel
    
    def configure_logger(self):
        if self.my_config.has_option("App", "log_level"):
            if self.my_config["App"]["log_level"] == "DEBUG":
                self.logger.setLevel(logging.DEBUG)