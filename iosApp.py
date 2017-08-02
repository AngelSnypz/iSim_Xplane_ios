from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock

from threading import Thread
from time import sleep

from kivy.lang import Builder

from kivy.app import App

from kivy.core.window import Window

from functools import partial

import csv

import xpc


class RootWidget(FloatLayout):
    def __init__(self):
        super(RootWidget, self).__init__()
        global client

        client = xpc.XPlaneConnect("127.0.0.1", 49009, 49010)
        sleep(1)
        event = Clock.schedule_interval(self.getVars, 1)
        event2 = Clock.schedule_interval(self.autoFail, 1)

    # reads vars from Xplane (need to uncomment to use)
    def getVars(self, dt):
        global airSpeed
        global altitude
        global timeRunning
        # timeRunning=client.getDREF('sim/time/total_running_time_sec')
        # airSpeed=client.getDREF('sim/flightmodel/position/true_airspeed')
        # altitude=client.getDREF('sim/flightmodel/misc/h_ind')

    # Code that runs every second checking for systems that have failed
    def autoFail(self, dt):
        for system in setFailures:
            print system
            if system[3] == 1:
                sw = system[4]
                spinner = system[5]
                spinner.text = 'Not Set'
                sw.active = True
                # actually fail the system
                client.sendDREF(system[0], 6)
                # need to remove failed system from setFailures list
                print system[0] + ' failed'

        setFailures[:] = (x for x in setFailures if x[3] == 0)

    # fixes all failures and resets UI (no easy way to do that)
    def fixAllSystems(self):
        client.repairAll()
        print 'all systems repaired'
        self.ids.fail_smoke_cockpit_switch.active = False
        self.ids.fail_door_open_switch.active = False
        self.ids.fail_external_power_switch.active = False
        self.ids.fail_passenger02_switch.active = False
        self.ids.fail_microburst_switch.active = False
        # self.ids.fail_smoke_button.state='normal'
        # self.ids.fail_door_button.state='normal'
        # self.ids.fail_externalpower_button.state='normal'
        # self.ids.fail_passenger02_button.state='normal'
        # self.ids.fail_microburst_button.state='normal'
        self.ids.fail_pilot_vertigo_button.state = 'normal'
        self.ids.fail_fuel_cap_button.state = 'normal'
        self.ids.fail_water_fuel_button.state = 'normal'
        self.ids.fail_wrong_fuel_button.state = 'normal'
        self.ids.fail_fuel_filter_button.state = 'normal'
        self.ids.fail_vasi_button.state = 'normal'
        self.ids.fail_runway_lights_button.state = 'normal'
        self.ids.fail_bird_strike_button.state = 'normal'
        self.ids.fail_brownout_button.state = 'normal'
        del setFailures[:]

    # simple method for handling slider input for weather primarily
    def sliderSystem(self, dref, val):
        client.sendDREF(dref, val)
        # print dref + "  " + str(val)

    # Method to handle setting failures to fail at specific conditions
    def setFails(self, spinner, switch):
        global timeRunning
        slider = Slider(min=0, max=400, id='slider_popup')
        label = Label(text=str(int(slider.value)))
        label2 = Label(text='stuff')
        box = BoxLayout(orientation='vertical')
        box2 = BoxLayout()

        box.add_widget(slider)
        box.add_widget(box2)
        box2.add_widget(label2)
        box2.add_widget(label)

        btn = Button(text='confirm', size_hint=(1, 0.5))
        box.add_widget(btn)
        popup = Popup(title='failure set',
                      content=box)
        btn.bind(on_press=popup.dismiss)

        # small handler method to capture slider changes
        def onSliderValChange(self, val):
            label.text = str(int(val))

        slider.bind(value=onSliderValChange)
        if spinner.text == 'Not Set':
            print 'removed set failures for : ' + switch.text
            for x in setFailures:
                if x[0] == switch.text:
                    x[3] = 2

        elif spinner.text == 'Fail at Speed':
            slider.max = 150
            label2.text = 'Speed (kts) To Fail System At: '
            btn.bind(on_press=lambda x: self.setToFail(slider.value, 'speed', switch, spinner))
            popup.open()
            print 'set ' + switch.text + ' to fail at speed'


        elif spinner.text == 'Fail at Altitude':
            slider.max = 40000
            label2.text = 'Altitude (m) To Fail System At: '
            btn.bind(on_press=lambda x: self.setToFail(slider.value, 'altitude', switch, spinner))
            popup.open()
            print 'set ' + switch.text + ' to fail at altitude'

        elif spinner.text == 'Fail at Time':
            slider.max = 600
            label2.text = 'Seconds To Fail System In: '
            btn.bind(on_press=lambda x: self.setToFail(slider.value + timeRunning[0], 'time', switch, spinner))
            popup.open()
            print 'set ' + switch.text + ' to fail at Time'

    def setToFail(self, val, failType, switch, spinner):
        failure = [switch.text, failType, int(val), 0, switch, spinner]
        setFailures.append(failure)

    # STILL NEED TO SORT THIS OUT - Should handle time slider and send it to the sim
    def setTime(self, dref, val):
        hours, minutes = val[:len(val) / 2], val[len(val) / 2:]
        # client.sendDREF(
        # print hours,minutes

    # Simple failure triggers for the on/off switches
    def failSystem2(self, switch):
        sw = switch
        if sw.active == True:
            client.sendDREF(switch.text, 6)
            print 'failed system: ' + switch.text
        elif sw.active == False:
            client.sendDREF(switch.text, 0)
            print 'fixed system: ' + switch.text

    # OLD - first version of above method - NEED TO DELETE LATER
    def failSystem(self, toggleButton, dref):
        tb = toggleButton
        if tb.state == 'down':
            print 'failing system:  ' + dref
            client.sendDREF(dref, 3)
        elif tb.state == 'normal':
            print 'fixing system: ' + dref
            client.sendDREF(dref, 0)

    # Simple Pause Command
    def pause(self):
        print "Pause Toggle"
        client.pauseXplane()

    # Simple Speed Increase/Decrease based on slider value
    def applySpeed(self, value):
        print value
        client.sendDREF("sim/time/sim_speed", value)

    # Searches csv file for airports are keys are pressed.
    def searchAirports(self, airportsearch):
        self.ids.results_scrollview.clear_widgets()
        csvfile = csv.reader(open('Airports.csv', 'rb'), delimiter=',')
        foundairports = {}
        found = 0
        for row in csvfile:

            if airportsearch.lower() in row[0].lower() or airportsearch.lower() in row[1].lower():
                foundairports[row[0]] = row[1]
                found = 1

        if found == 1:
            for x in foundairports:
                # x is the ICAO code
                # foundairports[x] is the Airport Name
                btn = Button(text=foundairports[x] + ' - ' + x, size_hint=(1, None),
                             size=(100, 75), font_size=20)
                btn.bind(on_press=partial(self.loadAirport, x))
                self.ids.results_scrollview.add_widget(btn)
            ''' else:
            popup=Popup(title='Airport Not Found',
                        content=Label(text='That airport was not found\n Touch anywhere outside of this popup to close it'),
                        size_hint=(0.5,0.5))
            popup.open()'''

    '''start selection via radio buttons can be done here. HOWEVER
    there is no way to check if an aiport has a helipad.
    it might be simpler to just default it to the runway
    and leave it up to the instructor to use the second screen
    to do the final movement (helipad/approach etc)
    '''

    # Simply Loads the airport based on what the user clicked in the search results
    def loadAirport(self, airportCode, *args):
        client.sendPREL(11, airportCode)
        print airportCode

    # Sets cloud layers from UI, 3 layers, multiple settings per layer
    def setClouds(self, togglebutton, cloudLayerHeightBot, cloudLayerHeightTop):
        tb = togglebutton
        if (tb.state == 'down'):
            # Need to send weather data to xplane here
            # Convert Group to layer
            # Convert Text to Type
            # Use sliderval for layer height
            cloudLayer = -1
            cloudType = -1

            if tb.group == '1':
                cloudLayer = 0
            elif tb.group == '2':
                cloudLayer = 1
            elif tb.group == '3':
                cloudLayer = 2
            else:
                print 'an error occurred'

            if tb.text == 'None':
                cloudType = 0
            elif tb.text == 'Cirrus':
                cloudType = 1
            elif tb.text == 'Scattered':
                cloudType = 2
            elif tb.text == 'Broken':
                cloudType = 3
            elif tb.text == 'Overcast':
                cloudType = 4
            else:
                print 'an error occurred'

            client.sendDREF('sim/weather/cloud_type[' + str(cloudLayer) + ']', cloudType)
            client.sendDREF('sim/weather/cloud_base_msl_m[' + str(cloudLayer) + ']', cloudLayerHeightBot)
            client.sendDREF('sim/weather/clout_tops_msl_m[' + str(cloudLayer) + ']', cloudLayerHeightTop)

    # Custom VKeyboard handler
    def keypress(self, key):
        if key == 'backspace':
            self.ids.search_input.do_cursor_movement('cursor_end', control=False, alt=False)
            self.ids.search_input.do_backspace(from_undo=False, mode='bkspc')
        else:
            self.ids.search_input.text += str(key)

        self.searchAirports(self.ids.search_input.text)

# Thread Process for checking for Failures based on a simple list
# Avoids locking up the UI
def checkFails():
    global setFailures
    global airSpeed
    global altitude
    global timeRunning
    while True:

        print airSpeed[0], altitude[0], timeRunning[0]
        # check each system
        for system in setFailures:
            if system[1] == 'speed':
                if airSpeed[0] > system[2]:
                    system[3] = 1
            elif system[1] == 'altitude':
                if altitude[0] > system[2]:
                    system[3] = 1
            elif system[1] == 'time':
                if timeRunning[0] > system[2]:
                    system[3] = 1

        # wait a second to avoid overpolling (might not be needed)
        sleep(1)


class iosApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    setFailures = []
    airSpeed = [0, ]
    altitude = [0, ]
    switch = [0, ]
    spinner = [0, ]
    timeRunning = [0, ]

    otherThread = Thread(target=checkFails)
    otherThread.start()
    iosApp().run()


