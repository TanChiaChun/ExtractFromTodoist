# Import packages
import sys
import logging
import ctypes

class MainException:
    def __init__(self, project_name, pLogger, log_string):
        self.project_name = project_name
        self.logger = pLogger
        self.log_string = log_string
    
    def handle_exception(self, log_message):
        complete_message = "App run fail!"
        self.logger.error(log_message, exc_info=True)
        self.logger.error(complete_message + self.log_string)
        ctypes.windll.user32.MessageBoxW(0, complete_message, self.project_name, 0) # Last 0 for OK
        sys.exit()