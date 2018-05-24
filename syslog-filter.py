#!/usr/bin/python

import sys
import re
import socket

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class LogEntry(object):
    """
        raw      : syslog entry as received from the syslog server
        resolved : syslog entry with the ip address resolved to name
        name     : FQDN
        ip       : ip address of the device
    """
    skip_wireless = ['Wireless', 'Radio', 'ssid', 'beacon', 'vap', 'WIRELESS', 'scan', 'SSID', 'radio', 'EAPOL', 'EAP',
                    'reassociated', 'bhp', 'deauthentication']
    
    skip_servers = ['TTY=unknown', 'RADIUS', 'anacron', '/IN', 'authoritative']

    skip_others = ['dhcpv6r', 'snmpmax']
 
    def __init__(self, line):
        # Store the syslog entry
        line = line.strip("\n")
        self.raw = line
        self.resolved = ""
        self.ip = ""
        self.name = ""
        self.domain = ""

        # Check if the sender its an ip address to be converted
        r1 = re.match("(.*)<(\S+)> (\d+).(\d+).(\d+).(\d+)(.*)", line)
        r2 = re.match("(.*)<(\S+)> (\S+)(.*)", line)
        if r1:
            ip = "%s.%s.%s.%s" % (r1.group(3), r1.group(4), r1.group(5), r1.group(6))
            try:
                #fqdn = socket.getfqdn(ip)
                #name, domain, cu = fqdn.split(".")
                # Avoid hammering the DNS
                name = ip
            except:
                name = ip
            self.resolved = "%s<%s> %s%s" % (r1.group(1), r1.group(2), name, r1.group(7))
            self.name = name
            self.ip = ip
        elif r2:
            try:
                # self.ip = socket.gethostbyname(r2.group(3))
                # Avoid hammering the DNS
                pass
            except: 
                self.ip = ""
            self.name = r2.group(3)
            self.resolved = line

        if self.name.startswith(("f","l","F","L")):
            self.domain = "Domain1"
        elif self.name.startswith(("u","r", "U","R")):
            self.domain = "Domain2"
        elif self.name.startswith(("p","t","P","T")):
            self.domain = "Domain3"

    def is_wireless(self):
        for s in LogEntry.skip_wireless:
            if s in self.raw:
                return True
        return False

    def is_server(self):
        for s in LogEntry.skip_servers:
            if s in self.raw:
                return True
        return False

    def is_others(self):
        for s in LogEntry.skip_others:
            if s in self.raw:
                return True
        return False

    def is_critic(self):
        l = ['Excessive', 'High', 'Fail', 'Failure']
        for s in l:
            if s in self.resolved:
                return True
        return False

    def print_log(self):
        print(self.resolved)

    def print_log_color(self, color):

        if color == "red":
            print bcolors.FAIL + self.resolved + bcolors.ENDC
        elif color == "blue":
            print bcolors.OKBLUE + self.resolved + bcolors.ENDC
        elif color == "green":
            print bcolors.OKGREEN + self.resolved + bcolors.ENDC
        return

if __name__ == "__main__":

    red_color = ['memory', 'High', 'Excessive']
    for line in sys.stdin:
        log = LogEntry(line)
        if log.is_wireless():
            continue
        if log.is_server():
            continue
        if log.is_others():
            continue
        else:
            if log.is_critic():
                log.print_log_color("red")    
            else:
                if log.domain == "Domain3":
                    log.print_log_color("blue")    
                elif log.domain == "Domain2":
                    log.print_log_color("green")    
                else:
                    log.print_log()

