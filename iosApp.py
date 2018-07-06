# coding=utf-8
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from threading import Thread
from time import sleep, time
import DebriefCap

from kivy.app import App
from functools import partial

import csv
import sys
import logging

import xpc


class RootWidget(FloatLayout):
    def __init__(self):
        super(RootWidget, self).__init__()
        global client
        global event1
        global start_time
        global current_time
        global elapsed_time
        elapsed_time=0
        current_time=0
        start_time=0

        success = 0

        # Connect the to the XPC plugin running inside xplane (localhost for same machine, other is for remote (ip will need to be changed to suit))
        client=xpc.XPlaneConnect("localhost", 49009,49010)
        #client = xpc.XPlaneConnect("192.168.1.7", 49009, 49010)

        # Looping to wait for the connection
        while success == 0:
            try:

                client.getDREF("sim/test/test_float")
                success = 1
            except:

                print 'Unable to Connect, retrying in 5s'
                sleep(5)

        # sleep to wait for setup, then setting clocks to tick to read data from xplane
        # and fail the set failures as needed
        # also handle the cloud layers based on the current UI state
        sleep(1)
        event1= Clock.schedule_interval(self.getVars, .1)
        event2= Clock.schedule_interval(self.autoFail, 1)
        event3= Clock.schedule_interval(self.cloudController,1)
        event4= Clock.schedule_interval(self.adaptiveUI,1)
        event5=Clock.schedule_interval(self.fuelLeak,1)

    def fuelLeak(self,dt):
        if(self.ids.fuel_leak_switch.active==True):
            currFuel=client.getDREF('sim/flightmodel/weight/m_fuel1')
            print str(currFuel) + " is current fuel"
            newFuel=currFuel[0]-5
            if(newFuel<=0): newFuel=0
            client.sendDREF('sim/flightmodel/weight/m_fuel1',newFuel)
            print str(newFuel) + " is new fuel"

    def adaptiveUI(self,dt):
        weightpercent = self.ids.weight_percent_label.text
        weightpercent2=weightpercent.split('%')



        if(int(weightpercent2[0])>=100):
            self.ids.weight_percent_label.color=[1,0,0,1]
            self.ids.weight_total_label.color=[1,0,0,1]
        else:
            self.ids.weight_percent_label.color = [1, 1, 1, 1]
            self.ids.weight_total_label.color = [1, 1, 1, 1]



    # reads vars from Xplane for use in checking failures etc
    def getVars(self, dt):
        global airSpeed
        global altitude
        global timeRunning
        global currentNG

        global start_time
        global current_time
        global elapsed_time


        current_time=time()
        disconnectThreshold=30
        skip=False

        try:
            airSpeed = client.getDREF('sim/flightmodel/position/true_airspeed')
            altitude = client.getDREF('sim/flightmodel/misc/h_ind')
            timeRunning = client.getDREF('sim/time/total_running_time_sec')
            currentNG=client.getDREF('AS350/VEMD/NG')
            if isinstance(App.get_running_app().root_window.children[0],Popup):
                if App.get_running_app().root_window.children[0].id=='Fails' or App.get_running_app().root_window.children[0].id=='QuitPopup' or App.get_running_app().root_window.children[0].id=='posPopup' :
                    pass
                else:
                    client.getDREF("sim/test/test_float")
                    App.get_running_app().root_window.children[0].dismiss()

            start_time=time()

        except:
            if isinstance(App.get_running_app().root_window.children[0], Popup) and skip==False:
                if App.get_running_app().root_window.children[0].id == 'Fails' or App.get_running_app().root_window.children[0].id == 'QuitPopup' or  App.get_running_app().root_window.children[0].id == 'posPopup':
                    if isinstance(App.get_running_app().root_window.children[1], Popup):
                        skip=True
            #else:


            if current_time-start_time>disconnectThreshold:
                exit("XPlane Shutdown/Not Responding")

            print "No Response from XPlane, Disconnecting in " + str(int(disconnectThreshold-(current_time-start_time)))


    # Hardcoded weather presets (modifying these is a laborious process
    def weatherPresets(self, weatherPreset):
        print weatherPreset
        CAVOK =         [0, 0, 0, 3048, 5486, 7924, 3657, 6096, 8534, 40233, 0, 0, 0, 29.92, 15240, 15240, 15240, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        VFR =           [0, 0, 0, 3048, 5486, 7924, 3657, 6096, 8534, 11265, 0, 0, 0, 29.92, 15240, 15240, 15240, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        MarginalVFR =   [4, 0, 0, 311, 5486, 7924, 920, 6096, 8534, 8046, 0, 0, 0, 29.92, 15240, 15240, 15240, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        NonPrecision =  [4, 0, 0, 128, 5486, 7924, 737, 6096, 8534, 4828, 0, 0, 0, 29.92, 15240, 15240, 15240, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        IFRCat1 =       [4, 0, 0, 67, 5486, 7924, 676, 6096, 8534, 804, 0, 0, 0, 29.92, 15240, 15240, 15240, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        IFRCat2 =       [4, 0, 0, 36, 5486, 7924, 646, 6096, 8534, 321, 0, 0, 0, 29.92, 15240, 15240, 15240, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        IFRCat3 =       [4, 0, 0, 21, 5486, 7924, 631, 6096, 8534, 160, 0, 0, 0, 29.92, 15240, 15240, 15240, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        Stormy =        [3, 0, 0, 240, 5486, 7924, 23000, 6096, 8534, 5000, 0.75, 0.75, 0, 29.92, 15240, 15240, 15240, 20, 20, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        drefs = ['sim/weather/cloud_type[0]',
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

        if weatherPreset == 'CAVOK':
            client.sendDREFs(drefs, CAVOK)
            self.weatherPresetUI(CAVOK)
        elif weatherPreset == 'VFR':
            client.sendDREFs(drefs, VFR)
            self.weatherPresetUI(VFR)
        elif weatherPreset == 'MarginalVFR':
            client.sendDREFs(drefs, MarginalVFR)
            self.weatherPresetUI(MarginalVFR)
        elif weatherPreset == 'NonPrecision':
            client.sendDREFs(drefs, NonPrecision)
            self.weatherPresetUI(NonPrecision)
        elif weatherPreset == 'IFRCat1':
            client.sendDREFs(drefs, IFRCat1)
            self.weatherPresetUI(IFRCat1)
        elif weatherPreset == 'IFRCat2':
            client.sendDREFs(drefs, IFRCat2)
            self.weatherPresetUI(IFRCat3)
        elif weatherPreset == 'IFRCat3':
            client.sendDREFs(drefs, IFRCat3)
            self.weatherPresetUI(IFRCat3)
        elif weatherPreset == 'Stormy':
            client.sendDREFs(drefs, Stormy)
            self.weatherPresetUI(Stormy)




            # update all of teh weather sliders to the new values

    # This Method is ridiculously Large, Only way to go about it afaik however
    def weatherPresetUI(self,vals):
        if vals[0]==0:
            self.ids.cloud1_none.state='down'
            self.ids.cloud1_cirrus.state = 'normal'
            self.ids.cloud1_scattered.state = 'normal'
            self.ids.cloud1_broken.state = 'normal'
            self.ids.cloud1_overcast.state = 'normal'
        elif vals[0]==1:
            self.ids.cloud1_none.state = 'normal'
            self.ids.cloud1_cirrus.state = 'down'
            self.ids.cloud1_scattered.state = 'normal'
            self.ids.cloud1_broken.state = 'normal'
            self.ids.cloud1_overcast.state = 'normal'
        elif vals[0]==2:
            self.ids.cloud1_none.state = 'normal'
            self.ids.cloud1_cirrus.state = 'normal'
            self.ids.cloud1_scattered.state = 'down'
            self.ids.cloud1_broken.state = 'normal'
            self.ids.cloud1_overcast.state = 'normal'
        elif vals[0]==3:
            self.ids.cloud1_none.state = 'normal'
            self.ids.cloud1_cirrus.state = 'normal'
            self.ids.cloud1_scattered.state = 'normal'
            self.ids.cloud1_broken.state = 'down'
            self.ids.cloud1_overcast.state = 'normal'
        elif vals[0]==4:
            self.ids.cloud1_none.state = 'normal'
            self.ids.cloud1_cirrus.state = 'normal'
            self.ids.cloud1_scattered.state = 'normal'
            self.ids.cloud1_broken.state = 'normal'
            self.ids.cloud1_overcast.state = 'down'


        if vals[1] == 0:
            self.ids.cloud2_none.state = 'down'
            self.ids.cloud2_cirrus.state = 'normal'
            self.ids.cloud2_scattered.state = 'normal'
            self.ids.cloud2_broken.state = 'normal'
            self.ids.cloud2_overcast.state = 'normal'
        elif vals[1] == 1:
            self.ids.cloud2_none.state = 'normal'
            self.ids.cloud2_cirrus.state = 'down'
            self.ids.cloud2_scattered.state = 'normal'
            self.ids.cloud2_broken.state = 'normal'
            self.ids.cloud2_overcast.state = 'normal'
        elif vals[1] == 2:
            self.ids.cloud2_none.state = 'normal'
            self.ids.cloud2_cirrus.state = 'normal'
            self.ids.cloud2_scattered.state = 'down'
            self.ids.cloud2_broken.state = 'normal'
            self.ids.cloud2_overcast.state = 'normal'
        elif vals[1] == 3:
            self.ids.cloud2_none.state = 'normal'
            self.ids.cloud2_cirrus.state = 'normal'
            self.ids.cloud2_scattered.state = 'normal'
            self.ids.cloud2_broken.state = 'down'
            self.ids.cloud2_overcast.state = 'normal'
        elif vals[1] == 4:
            self.ids.cloud2_none.state = 'normal'
            self.ids.cloud2_cirrus.state = 'normal'
            self.ids.cloud2_scattered.state = 'normal'
            self.ids.cloud2_broken.state = 'normal'
            self.ids.cloud2_overcast.state = 'down'


        if vals[2] == 0:
            self.ids.cloud3_none.state = 'down'
            self.ids.cloud3_cirrus.state = 'normal'
            self.ids.cloud3_scattered.state = 'normal'
            self.ids.cloud3_broken.state = 'normal'
            self.ids.cloud3_overcast.state = 'normal'
        elif vals[2] == 1:
            self.ids.cloud3_none.state = 'normal'
            self.ids.cloud3_cirrus.state = 'down'
            self.ids.cloud3_scattered.state = 'normal'
            self.ids.cloud3_broken.state = 'normal'
            self.ids.cloud3_overcast.state = 'normal'
        elif vals[2] == 2:
            self.ids.cloud3_none.state = 'normal'
            self.ids.cloud3_cirrus.state = 'normal'
            self.ids.cloud3_scattered.state = 'down'
            self.ids.cloud3_broken.state = 'normal'
            self.ids.cloud3_overcast.state = 'normal'
        elif vals[2] == 3:
            self.ids.cloud3_none.state = 'normal'
            self.ids.cloud3_cirrus.state = 'normal'
            self.ids.cloud3_scattered.state = 'normal'
            self.ids.cloud3_broken.state = 'down'
            self.ids.cloud3_overcast.state = 'normal'
        elif vals[2] == 4:
            self.ids.cloud3_none.state = 'normal'
            self.ids.cloud3_cirrus.state = 'normal'
            self.ids.cloud3_scattered.state = 'normal'
            self.ids.cloud3_broken.state = 'normal'
            self.ids.cloud3_overcast.state = 'down'

        self.ids.clouds_slider_1.value=vals[3]
        self.ids.clouds_slider_2.value = vals[4]
        self.ids.clouds_slider_3.value = vals[5]

        self.ids.clouds_slider_1_top.value=vals[6]
        self.ids.clouds_slider_2_top.value = vals[7]
        self.ids.clouds_slider_3_top.value = vals[8]

        self.ids.slider_visibility.value=vals[9]
        self.ids.slider_rain.value=vals[10]
        self.ids.slider_storm.value=vals[11]
        self.ids.slider_turbulence.value=vals[12]
        self.ids.slider_baro.value=vals[13]

        self.ids.winds_slider_altitude_1.value=vals[14]
        self.ids.winds_slider_altitude_2.value = vals[15]
        self.ids.winds_slider_altitude_3.value = vals[16]

        self.ids.winds_slider_direction_1.value=vals[17]
        self.ids.winds_slider_direction_2.value=vals[18]
        self.ids.winds_slider_direction_3.value=vals[19]

        self.ids.winds_slider_speed_1.value=vals[20]
        self.ids.winds_slider_speed_2.value=vals[21]
        self.ids.winds_slider_speed_3.value=vals[22]

        self.ids.winds_slider_sheardirection_1.value=vals[23]
        self.ids.winds_slider_sheardirection_2.value=vals[24]
        self.ids.winds_slider_sheardirection_3.value=vals[25]

        self.ids.winds_slider_shearspeed_1.value=vals[26]
        self.ids.winds_slider_shearspeed_2.value=vals[27]
        self.ids.winds_slider_shearspeed_3.value=vals[28]

        self.ids.winds_slider_turbulence_1.value=vals[29]
        self.ids.winds_slider_turbulence_2.value=vals[30]
        self.ids.winds_slider_turbulence_3.value=vals[31]

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
                #if len(system)==7:
                #   self.sendCommand(system[0])

                client.sendDREF(system[0], 6)
                # need to remove failed system from setFailures list
                print system[0] + ' failed'

        setFailures[:] = (x for x in setFailures if x[3] == 0)

    # fixes all failures and resets UI (no easy way to do that)
    def fixAllSystems(self):
        client.repairAll()
        print 'all systems repaired'
        self.ids.fail_smoke_cockpit_switch.active = False
        self.ids.fail_vasi_switch.active = False
        self.ids.fail_runway_lights_switch.active = False
        self.ids.fail_bird_strike_switch.active = False
        self.ids.fail_engine_flameout_switch.active = False
        self.ids.fail_engine_lost_power_switch.active = False
        self.ids.fail_oil_low_pres_switch.active = False
        self.ids.fail_eng_fire_switch.active = False
        self.ids.fail_eng_chip_switch.active = False
        self.ids.fail_engine_seize_switch.active = False
        self.ids.fail_battery_over_temp_switch.active = False
        self.ids.fail_battery_offline_switch.active = False
        self.ids.fail_gen_offline_switch.active = False
        self.ids.fail_electrical_bus_switch.active = False
        self.ids.fail_landing_light_switch.active = False
        self.ids.fail_pitot_blockage_switch.active = False
        self.ids.fail_static_blocked_switch.active = False
        self.ids.fail_static_heating_switch.active = False
        self.ids.fail_vsi_switch.active = False
        self.ids.fail_pitot_heating_inop_switch.active = False
        self.ids.fail_airspeed_indicator_switch.active = False
        self.ids.fail_artificial_horizon_switch.active = False
        self.ids.fail_altimeter_switch.active = False
        self.ids.fail_turn_indicator_switch.active = False
        self.ids.fail_directional_gyro_switch.active = False
        self.ids.fail_nav_1_switch.active = False
        self.ids.fail_nav_2_switch.active = False
        self.ids.fail_dme_switch.active = False
        self.ids.fail_localizer_switch.active = False
        self.ids.fail_glide_slope_switch.active = False
        self.ids.fail_g430_switch.active = False
        self.ids.fail_hung_start_switch.active = False
        self.ids.fail_ignitor_switch.active = False
        self.ids.fail_engine_starter_switch.active = False
        self.ids.fail_runway_itt_switch.active = False
        self.ids.fail_tail_rotor_effect_loss_switch.active = False
        self.ids.fail_major_gov_switch.active = False
        self.ids.fail_gov_fine_switch.active = False
        self.ids.fail_gov_coarse_switch.active = False
        self.ids.fail_driveshaft_switch.active = False
        self.ids.fail_fuel_lo_pres_switch.active = False
        self.ids.fail_fuel_filter_clog_switch.active = False
        self.ids.fail_hyd_pres_loss_switch.active = False
        self.ids.fail_hyd_overpressure_switch.active = False
        self.ids.fail_vemd_sc1_switch.active=False
        self.ids.fail_vemd_sc2_switch.active=False
        self.ids.fuel_leak_switch.active=False
        self.ids.fail_trq_indication_switch.active=False
        self.ids.fail_microburst_switch.active=False
        self.ids.fail_engine_fire_startup_switch.active=False
        self.ids.fail_mgb_hi_oil_temp_switch.active=False
        self.ids.fail_mgb_low_pres_switch.active=False

        self.ids.fail_mgb_low_pres_spinner.text='Not Set'
        self.ids.fail_mgb_hi_oil_temp_spinner.text='Not Set'
        self.ids.fail_engine_fire_startup_spinner.text='Not Set'
        self.ids.fail_microburst_spinner.text='Not Set'
        self.ids.fail_trq_indication_spinner.text='Not Set'
        self.ids.fuel_leak_spinner.text='Not Set'
        self.ids.fail_vemd_sc1_spinner.text='Not Set'
        self.ids.fail_vemd_sc1_spinner.text='Not Set'
        self.ids.fail_hyd_overpressure_spinner.text = 'Not Set'
        self.ids.fail_hyd_pres_loss_spinner.text = 'Not Set'
        self.ids.fail_fuel_filter_clog_spinner.text = 'Not Set'
        self.ids.fail_fuel_lo_pres_spinner.text = 'Not Set'
        self.ids.fail_driveshaft_spinner.text = 'Not Set'
        self.ids.fail_gov_coarse_spinner.text = 'Not Set'
        self.ids.fail_gov_fine_spinner.text = 'Not Set'
        self.ids.fail_major_gov_spinner.text = 'Not Set'
        self.ids.fail_tail_rotor_effect_loss_spinner.text = 'Not Set'
        self.ids.fail_runway_itt_spinner.text = 'Not Set'
        self.ids.fail_engine_starter_spinner.text = 'Not Set'
        self.ids.fail_ignitor_spinner.text = 'Not Set'
        self.ids.fail_hung_start_spinner.text = 'Not Set'
        self.ids.fail_g430_spinner.text = 'Not Set'
        self.ids.fail_glide_slope_spinner.text = 'Not Set'
        self.ids.fail_localizer_spinner.text = 'Not Set'
        self.ids.fail_dme_spinner.text = 'Not Set'
        self.ids.fail_nav_1_spinner.text = 'Not Set'
        self.ids.fail_nav_2_spinner.text = 'Not Set'
        self.ids.fail_directional_gyro_spinner.text = 'Not Set'
        self.ids.fail_turn_indicator_spinner.text = 'Not Set'
        self.ids.fail_altimeter_spinner.text = 'Not Set'
        self.ids.fail_artificial_horizon_spinner.text = 'Not Set'
        self.ids.fail_airspeed_indicator_spinner.text = 'Not Set'
        self.ids.fail_pitot_heating_inop_spinner.text = 'Not Set'
        self.ids.fail_vsi_spinner.text = 'Not Set'
        self.ids.fail_static_heating_spinner.text = 'Not Set'
        self.ids.fail_static_blocked_spinner.text = 'Not Set'
        self.ids.fail_pitot_blockage_spinner.text = 'Not Set'
        self.ids.fail_landing_light_spinner.text = 'Not Set'
        self.ids.fail_electrical_bus_spinner.text = 'Not Set'
        self.ids.fail_gen_offline_spinner.text = 'Not Set'
        self.ids.fail_battery_offline_spinner.text = 'Not Set'
        self.ids.fail_battery_over_temp_spinner.text = 'Not Set'
        self.ids.fail_smoke_cockpit_spinner.text = 'Not Set'

        self.ids.fail_microburst_spinner.text = 'Not Set'

        self.ids.fail_vasi_spinner.text = 'Not Set'
        self.ids.fail_runway_lights_spinner.text = 'Not Set'
        self.ids.fail_bird_strike_spinner.text = 'Not Set'
        self.ids.fail_engine_flameout_spinner.text = 'Not Set'
        self.ids.fail_engine_lost_power_spinner.text = 'Not Set'
        self.ids.fail_oil_low_pres_spinner.text = 'Not Set'
        self.ids.fail_eng_fire_spinner.text = 'Not Set'
        self.ids.fail_eng_chip_spinner.text = 'Not Set'
        self.ids.fail_engine_seize_spinner.text = 'Not Set'


        self.ids.fail_pitot_ice_slider.value = 0
        self.ids.fail_prop_ice_slider.value = 0
        self.ids.fail_inlet_ice_slider.value = 0

        del setFailures[:]


    def sliderSystem(self,dref,val):
        client.sendDREF(dref,val)
    # simple method for handling slider input for non-cloud weather settings primarily
    def sliderSystem2(self, slider,label):
        val=slider.value
        if(val<1):
            label.text='Wind Turbulence: None'
        elif(val>1 and val<=3):
            label.text='Wind Turbulence: Mild'
        elif(val>3 and val <=7):
            label.text='Wind Turbulence: Moderate'
        elif(val>7):
            label.text='Wind Turbulence: Severe'
        client.sendDREF(slider.text, val)
        # print dref + "  " + str(val)

    def failNavaid(self,navaidID):
        client.sendNfal(navaidID)


    # Method to handle setting failures to fail at specific conditions
    def setFails(self, spinner, switch):
        if('%' in spinner.text):
            if(spinner.text=='30% NG'):
                self.setToFail(30, 'NG', switch, spinner)
            elif (spinner.text == '40% NG'):
                self.setToFail(40, 'NG', switch, spinner)
            if (spinner.text == '50% NG'):
                self.setToFail(50, 'NG', switch, spinner)
        else:
        # popup setup code
            slider = Slider(min=0, max=400, id='slider_popup')
            label = Label(text=str(int(slider.value)), font_size=25)
            label2 = Label(text='stuff', font_size=25)
            box = BoxLayout(orientation='vertical')
            box3=BoxLayout()

            box2 = BoxLayout()

            box.add_widget(slider)
            box.add_widget(box2)
            box2.add_widget(label2)
            box2.add_widget(label)

            btn = Button(text='Confirm', size_hint=(1, 0.5), font_size=25)
            btn2 = Button(text='Cancel', size_hint=(1,0.5), font_size=25)

            box3.add_widget(btn)
            box3.add_widget(btn2)
            box.add_widget(box3)
            popup = Popup(title='failure set',
                          content=box, id='Fails')
            btn.bind(on_press=popup.dismiss)
            btn2.bind(on_press=popup.dismiss)

            # small handler method to capture slider changes
            def onSliderValChange(self, val):
                label.text = str(int(val))

            slider.bind(value=onSliderValChange)

            # code to handle the various options (fail at speed/alt/time) and display correctly
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

    # simple method to submit the failure to the threat maintaining the set failures
    def setToFail(self, val, failType, switch, spinner):
        failure = [switch.text, failType, int(val), 0, switch, spinner]
        setFailures.append(failure)

    # handle time slider and send it to the sim, also formats it to be human readable
    # The formatting needs to be set up correctly based on the size of the screen
    def setTime(self, dref, val,type):



        if (type == 'button'):
            self.ids.time_hours_slider.value = val
        elif (type=='slider'):
            time = val
            minutes = time / 60 % 60
            hours = time / 3600
            client.sendDREF(dref, time)
            if(hours<10 and minutes<10):
                self.ids.time_hours.text = 'Zulu Time:   0' + str(hours) + '0'+str(minutes)
            elif(minutes<10):
                self.ids.time_hours.text = 'Zulu Time:    ' + str(hours) +'0'+ str(minutes)
            elif(hours<10):
                self.ids.time_hours.text = 'Zulu Time:   0' + str(hours) + str(minutes)
            else:
                self.ids.time_hours.text = 'Zulu Time:    ' + str(hours) +str(minutes)

            localtimetuple = client.getDREF('sim/time/local_time_sec')

            localtime = int(localtimetuple[0])

            localMinutes = localtime / 60 % 60
            localHours = localtime / 3600
            if(localHours<10 and localMinutes<10):
                self.ids.local_time_hours.text = 'Local Time:   0' + str(localHours) +'0'+ str(localMinutes)
            elif(localHours<10):
                self.ids.local_time_hours.text = 'Local Time:   0' + str(localHours) + str(localMinutes)
            elif(localMinutes<10):
                self.ids.local_time_hours.text = 'Local Time:    ' + str(localHours) +'0'+ str(localMinutes)
            else:
                self.ids.local_time_hours.text = 'Local Time:    ' + str(localHours) + str(localMinutes)

            print(client.getDREF('AS350/VEMD/MODE'))

        # print hours,minutes

    # Simple failure triggers for the on/off switches
    def failSystem2(self, switch):
        sw = switch
        if sw.active == True:
            if(sw.text=="AS350/Hydraulic/Isolation"):
                client.sendDREF(switch.text,0)
            elif(sw.text=="enginepower"):
                origff=client.getDREF("sim/flightmodel/engine/ENGN_FF_")

                newff=origff[0]*0.8

                print(str(origff[0]) + " orig ff")
                print(str(newff) + " new ff")
                if(newff>0.05): newff=newff/3600
                client.sendDREF("sim/operation/override/override_fuel_flow",1)
                client.sendDREF("sim/operation/override/override_prop_pitch",1)


                client.sendDREF("sim/flightmodel/engine/ENGN_FF_",newff)

            else:
                client.sendDREF(switch.text, 6)
            print 'failed system: ' + switch.text

        elif sw.active == False:
            if(sw.text=="AS350/Hydraulic/Isolation"):
                client.sendDREF(switch.text,1)
            elif(sw.text=="enginepower"):
                client.sendDREF("sim/operation/override/override_fuel_flow",0)
                client.sendDREF("sim/operation/override/override_prop_pitch",0)

            else:
                client.sendDREF(switch.text, 0)
            print 'fixed system: ' + switch.text

    # Simple Pause Command
    def pause(self):
        print "Pause Toggle"
        client.pauseXplane()

    def quit(self):
        box = BoxLayout()
        box2=BoxLayout(orientation='vertical')
        txt = Label(text='Are you Sure you wish to Quit?', font_size=75)
        btn = Button(text='Confirm', size_hint=(1, 0.5), font_size=75)
        btn2 = Button(text='Cancel', size_hint=(1, 0.5), font_size=75)
        box.add_widget(btn)
        box.add_widget(btn2)
        box2.add_widget(txt)
        box2.add_widget(box)



        popup2 = Popup(title='Confirm Quit',
                      content=box2, id='QuitPopup', auto_dismiss=False)
        btn.bind(on_press=popup2.dismiss)
        btn2.bind(on_press=popup2.dismiss)
        btn.bind(on_press=self.quitConfirm)
        popup2.open()


    def quitConfirm(self,button):
        client.sendCommand("sim/operation/quit")
        sys.exit("Shutting Down")

    # Simple Speed Increase/Decrease based on slider value
    def applySpeed(self, value):
        print value
        client.sendDREF("sim/time/sim_speed", value)

    # Searches csv file for airports as keys are pressed.
    def searchAirports(self, airportsearch):
        try:
            self.ids.results_scrollview.clear_widgets()
            csvfile = csv.reader(open('Airports.csv', 'rb'), delimiter=',')
            foundairports = {}
            found = 0
            for row in csvfile:

                if airportsearch.lower() in row[0].lower() and airportsearch!='' or airportsearch.lower() in row[1].lower() and airportsearch!='':
                    foundairports[row[0]] = row[1]
                    found = 1

            if found == 1:
                for x in foundairports:
                    # x is the ICAO code
                    # foundairports[x] is the Airport Name
                    btn = Button(text=foundairports[x] + ' - ' + x, size_hint=(1, None),
                                 size=(100, 75), font_size=20)
                    btn.bind(on_press=partial(self.positionPopup, x))
                    self.ids.results_scrollview.add_widget(btn)
        except Exception:
            logging.exception("An Error Occurred")
            ''' else:
            popup=Popup(title='Airport Not Found',
                        content=Label(text='That airport was not found\n Touch anywhere outside of this popup to close it'),
                        size_hint=(0.5,0.5))
            popup.open()'''

    def engState(self,state,*args):
        if (state == 'on'):
            client.sendDREF('sim/operation/prefs/startup_running', 1)
        else:
            client.sendDREF('sim/operation/prefs/startup_running', 0)

    def positionPopup(self,airportCode, *args):

        box = BoxLayout(orientation='vertical')
        widget7 = Widget(size_hint=(0.2, 0.3))
        box.add_widget(widget7)

        box2 = BoxLayout()
        box3=BoxLayout()


        engoff=ToggleButton(text='Engine Not Running', group=10, allow_no_selection=False)
        engon=ToggleButton(text='Engine Running', group=10, state='down', allow_no_selection=False)
        engoff.bind(on_press=partial(self.engState,'off'))
        engon.bind(on_press=partial(self.engState,'on'))


        widget4 = Widget(size_hint=(0.2, 0.3))
        widget5 = Widget(size_hint=(0.2, 0.3))
        widget6 = Widget(size_hint=(0.2, 0.3))
        box3.add_widget(widget4)
        box3.add_widget(engoff)
        box3.add_widget(widget5)
        box3.add_widget(engon)
        box3.add_widget(widget6)
        box.add_widget(box3)
        widget8 =Widget(size_hint=(0.2, 0.3))
        box.add_widget(widget8)
        box.add_widget(box2)
        widget3 = Widget(size_hint=(0.2, 0.3))
        box.add_widget(widget3)
        popup=Popup(id='posPopup',title='Select Start', content=box,auto_dismiss=False)
        buttonAccept=Button(text='Confirm')
        buttonCancel=Button(text='Cancel')
        buttonCancel.bind(on_press=popup.dismiss)
        buttonAccept.bind(on_press=partial(self.loadAirport,airportCode,*args))
        buttonAccept.bind(on_press=popup.dismiss)
        widget=Widget(size_hint=(0.2, 0.3))
        widget1 = Widget(size_hint=(0.2, 0.3))
        widget2 = Widget(size_hint=(0.2, 0.3))
        box2.add_widget(widget)
        box2.add_widget(buttonAccept)
        box2.add_widget(widget1)
        box2.add_widget(buttonCancel)
        box2.add_widget(widget2)
        popup.open()



    # Simply Loads the airport based on what the user clicked in the search results
    def loadAirport(self, airportCode,*args):
        global event1
        waitLabel=Label(text='Please Wait whilst the sim loads')
        box = BoxLayout(orientation='vertical')
        box.add_widget(waitLabel)

        loading= Popup(title='Loading',
                      content=box, auto_dismiss=False)
        loading.open()

        event1.cancel()
        if(airportCode=='Carrier'):
            client.sendPREL(27, airportCode)
        elif(airportCode=='Frigate'):
            client.sendPREL(28, airportCode)
        elif (airportCode == 'Oil Rig Small'):
            client.sendPREL(29, airportCode)
        elif (airportCode == 'Oil Rig Large'):
            client.sendPREL(30, airportCode)
        else:
            client.sendACPR(11,airportCode)


        self.fixAllSystems()
        self.ids.search_input.text=''
        self.searchAirports('')
        event1 = Clock.schedule_interval(self.getVars, .1)

        print airportCode

    # takes a screencap of the map and prints it
    def printMap(self):
        DebriefCap.takeScreenshot()


    # method to change cloud layers, runs every 1s applying any changes necessary
    def cloudController(self,dt):

        cloudstate=0
        if self.ids.cloud1_none.state=='down': cloudstate=0
        elif self.ids.cloud1_cirrus.state=='down': cloudstate=1
        elif self.ids.cloud1_scattered.state=='down':cloudstate=2
        elif self.ids.cloud1_broken.state=='down':cloudstate=3
        elif self.ids.cloud1_overcast.state=='down':cloudstate=4
        cloudLayerHeightBot=self.ids.clouds_slider_1.value*0.3048
        cloudLayerHeightTop=self.ids.clouds_slider_1_top.value*0.3048
        client.sendDREF('sim/weather/cloud_type[0]', cloudstate)
        client.sendDREF('sim/weather/cloud_base_msl_m[0]', cloudLayerHeightBot)
        client.sendDREF('sim/weather/cloud_tops_msl_m[0]', cloudLayerHeightTop)


        cloudstate=0
        if self.ids.cloud2_none.state=='down': cloudstate=0
        elif self.ids.cloud2_cirrus.state=='down': cloudstate=1
        elif self.ids.cloud2_scattered.state=='down':cloudstate=2
        elif self.ids.cloud2_broken.state=='down':cloudstate=3
        elif self.ids.cloud2_overcast.state=='down':cloudstate=4
        cloudLayerHeightBot=self.ids.clouds_slider_2.value*0.3048
        cloudLayerHeightTop=self.ids.clouds_slider_2_top.value*0.3048
        client.sendDREF('sim/weather/cloud_type[1]', cloudstate)
        client.sendDREF('sim/weather/cloud_base_msl_m[1]', cloudLayerHeightBot)
        client.sendDREF('sim/weather/cloud_tops_msl_m[1]', cloudLayerHeightTop)


        cloudstate=0
        if self.ids.cloud3_none.state == 'down':cloudstate = 0
        elif self.ids.cloud3_cirrus.state == 'down': cloudstate = 1
        elif self.ids.cloud3_scattered.state == 'down': cloudstate = 2
        elif self.ids.cloud3_broken.state == 'down': cloudstate = 3
        elif self.ids.cloud3_overcast.state == 'down': cloudstate = 4
        cloudLayerHeightBot = self.ids.clouds_slider_3.value*0.3048
        cloudLayerHeightTop = self.ids.clouds_slider_3_top.value*0.3048
        client.sendDREF('sim/weather/cloud_type[2]', cloudstate)
        client.sendDREF('sim/weather/cloud_base_msl_m[2]', cloudLayerHeightBot)
        client.sendDREF('sim/weather/cloud_tops_msl_m[2]', cloudLayerHeightTop)

    def keypressNavaid(self,key):
        if key == 'backspace':
            self.ids.navaid_input.do_cursor_movement('cursor_end', control=False, alt=False)
            self.ids.navaid_input.do_backspace(from_undo=False, mode='bkspc')
        else:
            self.ids.navaid_input.text += str(key)
        self.searchNavaids(self.ids.navaid_input.text)

    def searchNavaids(self,searchItem):
        try:
            self.ids.results_scrollview_navaids.clear_widgets()
            csvfile = csv.reader(open('Airports1.csv', 'rb'), delimiter=',')
            foundNavaids = [[]] # 2d array of ICAO, String Name, Navaid ID
            found = 0
            count=0
            for row in csvfile:

                if searchItem.lower() in row[0].lower() and searchItem != '' or searchItem.lower() in row[1].lower() and searchItem != '' or searchItem.lower() in row[2].lower() and searchItem!='':
                    #foundNavaids.append([])
                    foundNavaids[count].append(row[0])
                    foundNavaids[count].append(row[1])
                    foundNavaids[count].append(row[2])
                    count=count+1
                    found = 1

            if found == 1:
                for x in foundNavaids:
                    btn = Button(text=x[0] + ' - ' +x[1] + ' - ' + x[2], size_hint=(1, None),
                                 size=(100, 75), fontx_size=20)
                    btn.bind(on_press=partial(self.failNavaid, x[2]))
                    self.ids.results_scrollview_navaids.add_widget(btn)
        except Exception:
            logging.exception("An Error Occurred")


    # Custom VKeyboard handler
    def keypress(self, key):
        # Special Case for backspace as focus is not maintained on the text input
        if key == 'backspace':
            self.ids.search_input.do_cursor_movement('cursor_end', control=False, alt=False)
            self.ids.search_input.do_backspace(from_undo=False, mode='bkspc')
        else:
            self.ids.search_input.text += str(key)

        # After each keypress the CSV is searched
        self.searchAirports(self.ids.search_input.text)

    def sendCommand(self,command):
        client.sendCommand(command)


# Thread Process for checking for Failures based on a simple list
# Avoids locking up the UI (might not be needed but better to be safe)
# Pythons Threading Capabilities are limited at best due to the GIL
# However this seems to work perfectly for the purpose ¯\_(ツ)_/¯
def checkFails():
    global setFailures
    global airSpeed
    global altitude
    global timeRunning
    global currentNG
    while True:

        # print airSpeed[0], altitude[0], timeRunning[0]
        # check each system
        for system in setFailures:
            if system[1] == 'speed':
                if airSpeed[0] == system[2] or (airSpeed[0] - system[2]) >= -2 and (airSpeed[0] - system[2]) <= 2:
                    system[3] = 1
            elif system[1] == 'altitude':
                if altitude[0] == system[2] or (altitude[0] - system[2]) >= -10 and (altitude[0] - system[2]) <= 10:
                    system[3] = 1
            elif system[1] == 'time':
                if timeRunning[0] == system[2] or (timeRunning[0] - system[2]) >= -1 and (
                    timeRunning[0] - system[2]) <= 1:
                    system[3] = 1

            elif system[1]=='NG':
                if currentNG[0]==system[2] or (currentNG[0] - system[2])>=-2 and (currentNG[0] - system[2]) <=2:
                    system[3]=1

        # wait a bit to avoid over-polling and unneeded CPU usage (~10-12% without the wait, 1-3% with a 0.1s sleep, Numbers from Laptop with i7-7700HQ)
        sleep(0.1)


class iosApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    Config.set('graphics','borderless','0')
    Config.set('graphics','position','custom')
    Config.set('graphics','height','1080')
    Config.set('graphics','width','1920')
    Config.set('graphics','left','0')

    # Container for failures that are set to happen
    setFailures = []

    # The values need to be in an array with val in pos 0, with a blank pos 1 due to how XPlane 11 returns the values
    airSpeed = [0, ]
    altitude = [0, ]
    switch = [0, ]
    spinner = [0, ]
    timeRunning = [0, ]
    engineNG=[0, ]

    # spawn the thread to handle the set failure checking, set it to be a daemon thread so it closes when the main thread does
    otherThread = Thread(target=checkFails)
    otherThread.daemon = True
    otherThread.start()

    # now everything is set up, launch the main thread
    try:
        iosApp().run()
    except Exception:
        logging.exception("Application Crash")
