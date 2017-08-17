from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock

from threading import Thread
from time import sleep

from kivy.app import App

from functools import partial

import csv

import xpc


class RootWidget(FloatLayout):
    def __init__(self):
        super(RootWidget, self).__init__()
        global client
        success=0
        client = xpc.XPlaneConnect("127.0.0.1", 49009, 49010)
        while(success==0):
            try:
                
                client.getDREF("sim/test/test_float")
                success=1
            except:

                print 'Unable to Connect, retrying in 5s'
                sleep(5)



        sleep(1)
        event = Clock.schedule_interval(self.getVars, 1)
        event2 = Clock.schedule_interval(self.autoFail, 1)


    # reads vars from Xplane (need to uncomment to use)
    def getVars(self, dt):
        global airSpeed
        global altitude
        global timeRunning
        #timeRunning=client.getDREF('sim/time/total_running_time_sec')
        #airSpeed=client.getDREF('sim/flightmodel/position/true_airspeed')
        #altitude=client.getDREF('sim/flightmodel/misc/h_ind')


    def weatherPresets(self,weatherPreset):
        print weatherPreset
        CAVOK =         [0,0,0,3048,5486,7924,3657,6096,8534,40233,   0,   0,0,29.92,15240,15240,15240,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0]
        VFR =           [0,0,0,3048,5486,7924,3657,6096,8534,11265,   0,   0,0,29.92,15240,15240,15240,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0]
        MarginalVFR =   [4,0,0, 311,5486,7924, 920,6096,8534, 8046,   0,   0,0,29.92,15240,15240,15240,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0]
        NonPrecision=   [4,0,0, 128,5486,7924, 737,6096,8534, 4828,   0,   0,0,29.92,15240,15240,15240,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0]
        IFRCat1=        [4,0,0,  67,5486,7924, 676,6096,8534,  804,   0,   0,0,29.92,15240,15240,15240,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0]
        IFRCat2=        [4,0,0,  36,5486,7924, 646,6096,8534,  321,   0,   0,0,29.92,15240,15240,15240,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0]
        IFRCat3=        [4,0,0,  21,5486,7924, 631,6096,8534,  160,   0,   0,0,29.92,15240,15240,15240,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0]
        Stormy=         [4,0,0,  67,5486,7924,5248,6096,8534,  804,0.75,0.75,0,29.92,15240,15240,15240,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0]
        drefs=['sim/weather/cloud_type[0]',
               'sim/weather/cloud_type[1]',
               'sim/weather/cloud_type[2]',
               'sim/weather/cloud_base_msl_m[0]',
               'sim/weather/cloud_base_msl_m[1]',
               'sim/weather/cloud_base_msl_m[2]',
               'sim/weather/cloud_tops_msl_m[0]',
               'sim/weather/cloud_tops_msl_m[1]',
               'sim/weather/cloud_tops_msl_m[2]',
               'sim/weather/visibility_reported_m',
               'sim/weather/rain_percent',
               'sim/weather/thunderstorm_percent',
               'sim/weather/wind_turbulence_percent',
               'sim/weather/barometer_sealevel_inhg',
               'sim/weather/wind_altitude_msl_m[0]',
               'sim/weather/wind_altitude_msl_m[1]',
               'sim/weather/wind_altitude_msl_m[2]',
               'sim/weather/wind_direction_degt[0]',
               'sim/weather/wind_direction_degt[1]',
               'sim/weather/wind_direction_degt[2]',
               'sim/weather/wind_speed_kt[0]',
               'sim/weather/wind_speed_kt[1]',
               'sim/weather/wind_speed_kt[2]',
               'sim/weather/shear_direction_degt[0]',
               'sim/weather/shear_direction_degt[1]',
               'sim/weather/shear_direction_degt[2]',
               'sim/weather/shear_speed_kt[0]',
               'sim/weather/shear_speed_kt[1]',
               'sim/weather/shear_speed_kt[2]',
               'sim/weather/turbulence[0]',
               'sim/weather/turbulence[1]',
               'sim/weather/turbulence[2]']

        if weatherPreset=='CAVOK':
            client.sendDREFs(drefs, CAVOK)
        elif weatherPreset=='VFR':
            client.sendDREFs(drefs,VFR)
        elif weatherPreset=='MarginalVFR':
            client.sendDREFs(drefs,MarginalVFR)
        elif weatherPreset=='NonPrecision':
            client.sendDREFs(drefs,NonPrecision)
        elif weatherPreset=='IFRCat1':
            client.sendDREFs(drefs,IFRCat1)
        elif weatherPreset=='IFRCat2':
            client.sendDREFs(drefs,IFRCat2)
        elif weatherPreset=='IFRCat3':
            client.sendDREFs(drefs,IFRCat3)
        elif weatherPreset=='Stormy':
            client.sendDREFs(drefs,Stormy)

        #update all of teh weather sliders to the new values

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
        self.ids.fail_vertigo_switch.active=False
        self.ids.fail_water_fuel_switch.active=False
        self.ids.fail_wrong_fuel_switch.active=False
        self.ids.fail_vasi_switch.active=False
        self.ids.fail_runway_lights_switch.active=False
        self.ids.fail_bird_strike_switch.active=False
        self.ids.fail_engine_flameout_switch.active=False
        self.ids.fail_engine_lost_power_switch.active=False
        self.ids.fail_oil_over_temp_switch.active=False
        self.ids.fail_oil_low_pres_switch.active=False
        self.ids.fail_eng_fire_switch.active=False
        self.ids.fail_eng_fadec_switch.active=False
        self.ids.fail_twt_grip_switch.active=False
        self.ids.fail_eng_chip_switch.active=False
        self.ids.fail_main_gbox_low_oil_pres_switch.active=False
        self.ids.fail_main_gbox_oil_overheat_switch.active=False
        self.ids.fail_bleed_valve_switch.active=False
        self.ids.fail_fuel_flow_fluctuation_switch.active=False
        self.ids.fail_compressor_stall_switch.active=False
        self.ids.fail_engine_seize_switch.active=False
        self.ids.fail_engine_fuel_pump_switch.active=False
        self.ids.fail_fuel_filter_switch.active=False
        self.ids.fail_battery_over_temp_switch.active=False
        self.ids.fail_battery_offline_switch.active=False
        self.ids.fail_gen_offline_switch.active=False
        self.ids.fail_instrument_light_switch.active=False
        self.ids.fail_electrical_bus_switch.active=False
        self.ids.fail_landing_light_switch.active=False
        self.ids.fail_pitot_blockage_switch.active=False
        self.ids.fail_static_blocked_switch.active=False
        self.ids.fail_static_heating_switch.active=False
        self.ids.fail_vsi_switch.active=False
        self.ids.fail_pitot_heating_inop_switch.active=False
        self.ids.fail_airspeed_indicator_switch.active=False
        self.ids.fail_artificial_horizon_switch.active=False
        self.ids.fail_altimeter_switch.active=False
        self.ids.fail_turn_indicator_switch.active=False
        self.ids.fail_directional_gyro_switch.active=False
        self.ids.fail_nav_1_switch.active=False
        self.ids.fail_nav_2_switch.active = False
        self.ids.fail_dme_switch.active=False
        self.ids.fail_localizer_switch.active=False
        self.ids.fail_glide_slope_switch.active=False
        self.ids.fail_vvi_switch.active=False
        self.ids.fail_g430_switch.active=False
        self.ids.fail_transponder_switch.active=False
        self.ids.fail_hung_start_switch.active=False
        self.ids.fail_ignitor_switch.active=False
        self.ids.fail_engine_starter_switch.active=False
        self.ids.fail_hot_start_switch.active=False
        self.ids.fail_runway_itt_switch.active=False
        self.ids.fail_rudder_trim_runaway_switch.active=False
        self.ids.fail_rudder_trim_switch.active=False
        self.ids.fail_tail_rotor_effect_loss_switch.active=False
        self.ids.fail_major_gov_switch.active=False
        self.ids.fail_gov_fine_switch.active=False
        self.ids.fail_gov_coarse_switch.active=False
        self.ids.fail_driveshaft_switch.active=False
        self.ids.fail_fuel_lo_pres_switch.active=False
        self.ids.fail_fuel_filter_clog_switch.active=False
        self.ids.fail_hyd_pres_loss_switch.active=False
        self.ids.fail_yaw_damper_switch.active=False
        self.ids.fail_hyd_overpressure_switch.active=False

        self.ids.fail_hyd_overpressure_spinner.text='Not Set'
        self.ids.fail_yaw_damper_spinner.text='Not Set'
        self.ids.fail_hyd_pres_loss_spinner.text='Not Set'
        self.ids.fail_fuel_filter_clog_spinner.text='Not Set'
        self.ids.fail_fuel_lo_pres_spinner.text='Not Set'
        self.ids.fail_driveshaft_spinner.text='Not Set'
        self.ids.fail_gov_coarse_spinner.text='Not Set'
        self.ids.fail_gov_fine_spinner.text='Not Set'
        self.ids.fail_major_gov_spinner.text='Not Set'
        self.ids.fail_tail_rotor_effect_loss_spinner.text='Not Set'
        self.ids.fail_rudder_trim_spinner.text='Not Set'
        self.ids.fail_rudder_trim_runaway_spinner.text='Not Set'
        self.ids.fail_runway_itt_spinner.text='Not Set'
        self.ids.fail_hot_start_spinner.text='Not Set'
        self.ids.fail_engine_starter_spinner.text='Not Set'
        self.ids.fail_ignitor_spinner.text='Not Set'
        self.ids.fail_hung_start_spinner.text='Not Set'
        self.ids.fail_transponder_spinner.text='Not Set'
        self.ids.fail_g430_spinner.text='Not Set'
        self.ids.fail_vvi_spinner.text='Not Set'
        self.ids.fail_glide_slope_spinner.text='Not Set'
        self.ids.fail_localizer_spinner.text='Not Set'
        self.ids.fail_dme_spinner.text='Not Set'
        self.ids.fail_nav_1_spinner.text='Not Set'
        self.ids.fail_nav_2_spinner.text = 'Not Set'
        self.ids.fail_directional_gyro_spinner.text='Not Set'
        self.ids.fail_turn_indicator_spinner.text='Not Set'
        self.ids.fail_altimeter_spinner.text='Not Set'
        self.ids.fail_artificial_horizon_spinner.text='Not Set'
        self.ids.fail_airspeed_indicator_spinner.text='Not Set'
        self.ids.fail_pitot_heating_inop_spinner.text='Not Set'
        self.ids.fail_vsi_spinner.text='Not Set'
        self.ids.fail_static_heating_spinner.text='Not Set'
        self.ids.fail_static_blocked_spinner.text='Not Set'
        self.ids.fail_pitot_blockage_spinner.text='Not Set'
        self.ids.fail_landing_light_spinner.text='Not Set'
        self.ids.fail_electrical_bus_spinner.text='Not Set'
        self.ids.fail_instrument_light_spinner.text='Not Set'
        self.ids.fail_gen_offline_spinner.text='Not Set'
        self.ids.fail_battery_offline_spinner.text='Not Set'
        self.ids.fail_battery_over_temp_spinner.text='Not Set'
        self.ids.fail_fuel_filter_spinner.text='Not Set'
        self.ids.fail_smoke_cockpit_spinner.text='Not Set'
        self.ids.fail_door_open_spinner.text='Not Set'
        self.ids.fail_external_power_spinner.text='Not Set'
        self.ids.fail_passenger02_spinner.text='Not Set'
        self.ids.fail_microburst_spinner.text='Not Set'
        self.ids.fail_vertigo_spinner.text='Not Set'
        self.ids.fail_water_fuel_spinner.text='Not Set'
        self.ids.fail_wrong_fuel_spinner.text='Not Set'
        self.ids.fail_vasi_spinner.text='Not Set'
        self.ids.fail_runway_lights_spinner.text='Not Set'
        self.ids.fail_bird_strike_spinner.text='Not Set'
        self.ids.fail_engine_flameout_spinner.text='Not Set'
        self.ids.fail_engine_lost_power_spinner.text='Not Set'
        self.ids.fail_oil_over_temp_spinner.text='Not Set'
        self.ids.fail_oil_low_pres_spinner.text='Not Set'
        self.ids.fail_eng_fire_spinner.text='Not Set'
        self.ids.fail_eng_fadec_spinner.text='Not Set'
        self.ids.fail_twt_grip_spinner.text='Not Set'
        self.ids.fail_eng_chip_spinner.text='Not Set'
        self.ids.fail_main_gbox_low_oil_pres_spinner.text='Not Set'
        self.ids.fail_main_gbox_oil_overheat_spinner.text='Not Set'
        self.ids.fail_bleed_valve_spinner.text='Not Set'
        self.ids.fail_fuel_flow_fluctuation_spinner.text='Not Set'
        self.ids.fail_compressor_stall_spinner.text='Not Set'
        self.ids.fail_engine_seize_spinner.text='Not Set'
        self.ids.fail_engine_fuel_pump_spinner.text='Not Set'


        self.ids.fail_pitot_ice_slider.value=0
        self.ids.fail_prop_ice_slider.value=0
        self.ids.fail_inlet_ice_slider.value=0



        del setFailures[:]

    # simple method for handling slider input for weather primarily
    def sliderSystem(self, dref, val):
        client.sendDREF(dref, val)
        # print dref + "  " + str(val)

    # Method to handle setting failures to fail at specific conditions
    def setFails(self, spinner, switch):

        slider = Slider(min=0, max=400, id='slider_popup')
        label = Label(text=str(int(slider.value)),font_size=25)
        label2 = Label(text='stuff',font_size=25)
        box = BoxLayout(orientation='vertical')
        box2 = BoxLayout()

        box.add_widget(slider)
        box.add_widget(box2)
        box2.add_widget(label2)
        box2.add_widget(label)

        btn = Button(text='Confirm', size_hint=(1, 0.5),font_size=25)
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

    # handle time slider and send it to the sim, also formats it to be human readable
    def setTime(self, dref, val):
        time=val
        minutes=time/60 % 60
        hours =time/3600
        self.ids.time_minutes.text=str(minutes)
        self.ids.time_hours.text='Zulu Time:   ' + str(hours) + ' : '

        client.sendDREF(dref,time)
        localtimetuple= client.getDREF('sim/time/local_time_sec')

        localtime=int(localtimetuple[0])
        print localtime, time
        localMinutes = localtime/60%60
        localHours=localtime/3600
        self.ids.local_time_minutes.text=str(localMinutes)
        self.ids.local_time_hours.text='Local Time:   ' + str(localHours) +' : '
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

    # Simply Loads the airport based on what the user clicked in the search results
    def loadAirport(self, airportCode, *args):
        client.sendPREL(11, airportCode)
        self.fixAllSystems()
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
# Avoids locking up the UI (maybe?)
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
                if airSpeed[0] == system[2] or (airSpeed[0]-system[2])>=-1 and (airSpeed[0]-system[2])<=1:
                    system[3] = 1
            elif system[1] == 'altitude':
                if altitude[0] == system[2] or (altitude[0]-system[2])>=-1 and (altitude[0]-system[2])<=1 :
                    system[3] = 1
            elif system[1] == 'time':
                if timeRunning[0] == system[2] or (timeRunning[0]-system[2]) >=-1 and  (timeRunning[0]-system[2]) <=1 :
                    system[3] = 1

        # wait a bit to avoid over-polling and unneeded CPU usage (~10-12% without the wait, 1-3% with a 0.1s sleep)
        sleep(0.1)


class iosApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    setFailures = []

    #The values need to be in an array with val in pos 0, with a blank pos 1 due to how XPlane 11 returns the values
    airSpeed = [0, ]
    altitude = [0, ]
    switch = [0, ]
    spinner = [0, ]
    timeRunning = [0, ]

    otherThread = Thread(target=checkFails)
    otherThread.daemon=True
    otherThread.start()
    iosApp().run()


