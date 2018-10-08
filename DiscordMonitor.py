import os
import configparser
import sys
import threading
import time
import sched
import atexit
from shutil import copyfile

from pyfirmata import Arduino
import discord
from ShiftOut import ShiftOut
from Status import *

import SysTrayIcon

REFRESH = 0.5


class DiscordMonitor:
    def __init__(self):
        self.client = discord.Client()

        # Extract data from config file
        self.config = configparser.ConfigParser()
        if not os.path.isfile("config.ini"):
            copyfile("default.ini", "config.ini")
        self.config.read("config.ini")
        self.username = self.config['LoginInfo']['Email']
        self.password = self.config['LoginInfo']['Password']

        # Initialize Arduino
        comm = Arduino('COM3')
        latchPin = int(self.config['Pins']['latchPin'])
        clockPin = int(self.config['Pins']['clockPin'])
        dataPin = int(self.config['Pins']['dataPin'])
        self.monitor = ShiftOut(comm, dataPin, latchPin, clockPin)

        # Clear board
        self.monitor.ShiftOut(0x00)

        self.threads = {}

        # Schedule callback
        self.sched = sched.scheduler(time.time, time.sleep)
        self.sched.enter(REFRESH, 1, self.update)
        t_sched = threading.Thread(target=self.sched.run, daemon=True)
        t_sched.start()
        self.threads['t_sched'] = t_sched

        def run_tray_icon(): SysTrayIcon.SysTrayIcon('dm.ico', 'Discord Monitor', (),
                                    on_quit=lambda *_: self.exit())

        # Set up Tray Icon to keep other threads running
        # Exits when only daemon threads left
        t_tray = threading.Thread(target=run_tray_icon, daemon=False)
        t_tray.start()
        self.threads['t_tray'] = t_tray

        # Log into Discord
        self.login()

    def update(self):
        # Disconnected
        status = DISCONNECTED
        if self.client.is_logged_in:
            status |= CONNECTED
            for server in self.client.servers:
                member_id = server.get_member(self.client.user.id)
                member_voice = member_id.voice
                if member_voice is not None:
                    if member_voice.deaf or member_voice.self_deaf:
                        status |= DEAFENED
                        break
                    elif member_voice.mute or member_voice.self_mute:
                        status |= MUTED
                        break
        self.monitor.ShiftOut(status)
        self.sched.enter(REFRESH, 1, self.update)

    def login(self):
        print("Attempting to log in as {}...".format(self.username))
        # Checks if script is already running
        if self.threads.get("t_client"):
            print('Duplicate login')
            self.client.logout()
        t_client = threading.Thread(target=self.client.run, args=(self.username, self.password), daemon=True)
        t_client.start()
        self.threads['t_client'] = t_client

    def exit(self):
        print('Exiting...')
        sys.exit()


def main():
    monitor = DiscordMonitor()
    atexit.register(monitor.exit)


if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            pass
        else:
            break
