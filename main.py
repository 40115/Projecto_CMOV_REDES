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

Pin_12='P12'
Pin_16='P16'
pwm_12 = PWM(0, frequency=50)
pwm_c12 = pwm_12.channel(0, pin=Pin_12, duty_cycle=0.05)
adc = ADC(0)
adc.vref(1120)
authorization_Key = 'HMSRJMTN97XVL8VW'
Http_Update_host = 'https://api.thingspeak.com/'
ssid = 'Vodafone-Pinto'
net_key = 'helenaruben64'

mosquitto_ip = "mqtt3.thingspeak.com"
    #Connect to mosquito
mosquitto_port = 1883
device_id = "NiYOAQgOICktLjosKCEFIQY"
mosquitto_uname="NiYOAQgOICktLjosKCEFIQY"
mosquitto_pass="dl3b/+K57J++iZ4ffxtJ4/dF"
mqttclient=None
channel_id="1998372"

def sub_cb(topic, msg):
   print("sub_cb(): received on topic={} the msg={}\n".format(topic.decode(), msg.decode()))

def init_mqtt():
    value=read_light()
    value=4095-value
    value=int(value*100/4095)
    print(value)
    connect_to_wifi_network_wap2(wlan_mode=WLAN.STA,net_ssid=ssid, key=net_key)
    mqttclient_Connect(value)
    pwm_c12 = pwm_12.channel(0, pin=Pin_12, duty_cycle=0.05)
    #pwm_c.duty_cycle(0.09 ) # change the duty cycle to 30%
    #mqttclient_pushing(value)

def init():
    value=read_light()
    value=4095-value
    value=int(value*100/4095)
    print(value)
    connect_to_wifi_network_wap2(wlan_mode=WLAN.STA,net_ssid=ssid, key=net_key)
    pwm_c12 = pwm_12.channel(0, pin=Pin_12, duty_cycle=0.05)
    #pwm_c.duty_cycle(0.09 ) # change the duty cycle to 30%
    get_http_call(Http_Update_host,value)

def rancheckwifi():
    while True:
        value=read_light()
        value=4095-value
        value=int(value*100/4095)
        print(value)
        pwm_c12 = pwm_12.channel(0, pin=Pin_12, duty_cycle=0.05)
        #pwm_c.duty_cycle(0.09 ) # change the duty cycle to 30%
        get_http_call(Http_Update_host,value)
        checkservocurtina(value)
        time.sleep(5)

def rancheckmqtt():
    while True:
        value=read_light()
        value=4095-value
        value=int(value*100/4095)
        print(value)
        pwm_c12 = pwm_12.channel(0, pin=Pin_12, duty_cycle=0.05)
        #pwm_c.duty_cycle(0.09 ) # change the duty cycle to 30%
        #get_http_call(Http_Update_host,value)
        mqttclient_pushing(value)
        checkservocurtina(value)
        time.sleep(5)

def mqttclient_Connect(value):

    print('main(): create MQTT client to broker on addr = {}, port = {}...'.format(mosquitto_ip, mosquitto_port))
    mqttclient = MQTTClient(device_id, mosquitto_ip, user=mosquitto_uname, password=mosquitto_pass, port=mosquitto_port)
    #mqttclient = MQTTClient(device_id, mosquitto_ip, port=mosquitto_port)
    try:
        print('main(): set callback and connect to broker...')
        ##Set a callback listening a topic
        mqttclient.set_callback(sub_cb)
        mqttclient.connect()
        topic = "channels/" + channel_id + "/publish"
        tpayload="field1="+str(value)+"&status=MQTTPUBLISH"
        print("main(): Sending sensorvalue={}".format(value))
        mqttclient.publish(topic=topic, msg="{"+tpayload+"}")
    except OSError as err:
        print('main(): cannot connect to broker on addr = {} with err = {}...\n'.format(mosquitto_ip, err))

def mqttclient_pushing(values):
    pass



def checkservocurtina(value=100):
    if value<30:
        pwm_c12.duty_cycle(0.1 )
        time.sleep(1)
        pwm_c12.duty_cycle(0.05 )

def get_http_call(url=Http_Update_host,value=-1):
    try:
        tesr="{}update?api_key={}&field1={}".format(url, authorization_Key, str(value) )
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
    #init()
    #rancheckwifi()
    init_mqtt()



if __name__ == "__main__":
    main()
