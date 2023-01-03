# file: main.py
import pycom
import sys
import time
import os
import machine
import urequests as requests #urequests placed into *lib* directory
from network import WLAN
import ujson
import ufun
import time
from mqtt import MQTTClient
from wificon import WiFiClient
from machine import ADC, Pin, PWM
import utime


pwm_12 = PWM(0, frequency=50)
Pin_12='P12'
Pin_16='P16'
adc = ADC(0)
adc.vref(1120)
authorization_Key = 'HMSRJMTN97XVL8VW'
Http_Update_host = 'https://api.thingspeak.com/'

ssid = 'Vodafone-Pinto'
net_key = 'helenaruben64'

def init():
    value=read_light()
    value=4095-value
    value=int(value*100/4095)
    print(value)
    connect_to_wifi_network_wap2(wlan_mode=WLAN.STA,net_ssid=ssid, key=net_key)
    pwm_c = pwm_12.channel(0, pin=Pin_12, duty_cycle=0.05)
    #pwm_c.duty_cycle(0.09 ) # change the duty cycle to 30%
    get_http_call(Http_Update_host,value)

def ran_check_Wifi()
    while True:
        value=read_light()
        value=4095-value
        value=int(value*100/4095)
        print(value)
        pwm_c = pwm_12.channel(0, pin=Pin_12, duty_cycle=0.05)
        #pwm_c.duty_cycle(0.09 ) # change the duty cycle to 30%
        get_http_call(Http_Update_host,value)
        check_Servo_Curtina(value)
        time.sleep(5)

def check_Servo_Curtina(value=100)
    if value<30:
        pwm_c.duty_cycle(0.1 )
        time.sleep(1)
        pwm_c.duty_cycle(0.05 )

def get_http_call(url=Http_Update_host,value=-1):
    try:
        Test="2020/10/10T20:20:20"
        tesr="{}update?api_key={}&field1={}&field2={}".format(url, authorization_Key, str(value),Test )
        # Content-Type HTTP header should be set only for PUT and POST requests
        request = requests.get(tesr)
        reply=request.content.decode()
        # Finally, close response objects to avoid resource leaks and malfunction
        print(tesr)
        return ""
    except Exception as e:
        print(e)
    return "ff"

def post_http_call(url='http://homepage.ufp.pt/rmoreira/LP2/data.txt',value=""):
    try:
        data = {'api_dev_key':value
        }
        # Content-Type HTTP header should be set only for PUT and POST requests
        request = requests.get(url)
        reply=request.content.decode()
        print("get_http_call(): content="+request.content.decode())
        print("get_http_call(): text="+request.text)

        # Finally, close response objects to avoid resource leaks and malfunction
        request.close()
        return request.json()
    except Exception as e:
        print(e)
    return "ff"

def read_light():
    adc_channel_pin  = adc.channel(pin=Pin_16, attn=ADC.ATTN_11DB)
    values = adc_channel_pin.value()
    return values

def connect_to_wifi_network_wap2(wlan_mode=WLAN.STA, net_ssid='ssid', sec_proto=WLAN.WPA2, key='wpa2key', timeout=10000):
    print("connect_to_wifi_network_dhcp(net_ssid={}):...".format(net_ssid))
    """ To retrieve the current WLAN instance """
    # The WLAN network class boots in WLAN.AP mode
    #wlan = WLAN()
    # The WLAN net class can boot as STAtion (connect to an existing network)
    wlan = WLAN(mode=wlan_mode)
    print("connect_to_wifi_network_dhcp(): WLAN mode: {}".format(wlan.mode()))

    #Connecting to a Router... Scan for networks:
    nets = wlan.scan()
    for net in nets:
        if net.ssid == net_ssid:
            print("connect_to_wifi_network_dhcp(): Network {} found!".format(net.ssid))
            wlan.connect(ssid=net.ssid, auth=(sec_proto, key), timeout=timeout)
            while not wlan.isconnected():
                machine.idle() # save power while waiting
            print("connect_to_wifi_network_dhcp(): WLAN connection {} success!".format(net_ssid))
            break

def main():
    print("Hello World!")
    init()




if __name__ == "__main__":
    main()
