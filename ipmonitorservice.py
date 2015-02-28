# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText
#get public ip from opening site
from urllib.request import urlopen

#get ip function, returns false with no connection
def checkip():
    try:
        response=urlopen('http://arekusanda.com/ip/iptest.php',timeout=1).read()
        return response
    except URLError as err: pass
    return False

#msg details
def sendEmail(message):
    msg = {}
    msg['Subject'] = 'IP location'
    msg['From'] = 'EMAIL_ADDRESS@EMAIL.COM'
    msg['To'] = 'RECIPIENTS_EMAIL@EMAIL.COM'
    msg['msg'] = ip
    pw = 'FROM_EMAIL_PW'
    # SMTP server
    server = smtplib.SMTP('SMTP_SERVER:PORT')
    server.ehlo()
    server.starttls()
    #username, pw
    server.login(msg['From'],pw)
    #from, to, msg
    server.sendmail(msg['From'],msg['To'],message)
    server.quit()


### Run Python scripts as a service example from ryrobes.com
### Usage : python ipmonitorservice.py install (or / then start, stop, remove)
import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import os, sys, string, time

class ipmonitorservice(win32serviceutil.ServiceFramework):
	#Name the service and give it a description and display name
    _svc_name_ = "IPmonitorService"
    _svc_display_name_ = "IP Python Security Daemon"
    _svc_description_ = "Personal Security Monitoring"
         
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)          

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)                    
         
    def SvcDoRun(self):
        import servicemanager      
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
     
        #self.timeout = 640000    #640 seconds / 10 minutes (value is in milliseconds)
        self.timeout = 60000     
        # This is how long the service will wait to run / refresh itself (see script below)
        while 1:
            # Wait for service stop signal, if I timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal encountered
				infomsg = _svc_name_ + " - STOPPED"
                servicemanager.LogInfoMsg(infomsg)  #For Event Log
                break
            else:
                #Ok, here's the real money shot right here.
                #[actual service code between rests]
                try:
                    #Execute code here
                    ip = checkip().decode()
                    if ip != False:
                        sendEmail(ip)
                        break #stop service
                except:
                    pass
                 #[actual service code between rests]


def ctrlHandler(ctrlType):
    return True
                 
if __name__ == '__main__':  
    win32api.SetConsoleCtrlHandler(ctrlHandler, True)  
    win32serviceutil.HandleCommandLine(ipmonitorservice)
