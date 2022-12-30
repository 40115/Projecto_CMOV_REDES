# file: main.py
import pycom
import sys
import time
import os
import machine
from network import WLAN
import ujson
import ufun
from mqtt import MQTTClient
from wificon import WiFiClient


"""
 * // The main.py script runs directly after boot.py and should contain the main code to run on device.
 * // - The code may be executed with the *run* command;
 * // - The code will not remain on the device permanently (reboot will be wiped it);
 * // - We may upload it permanently using *upload* command.
 * // - The code will only work with libraries available in the firmware;
 * 
 * // To check lopy4 firmware version:
 * >>> import os
 * >>> os.uname()
 * // OR
 * >>> import sys
 * >>> sys.version
 * >>> sys.platform
 * >>> sys.implementation
 *
 * // To remove files from device:
 * // - Format device’s internal flash python script:
 * >>> import os
 * >>> os.fsformat('/flash')
 * 
 * //======= RESET from within a script: =======
 * // Soft reset clears the state of the MicroPython VM but leaves hardware peripherals unaffected.
 * // On REPL (Read–Eval–Print Loop):
 * >>> Ctrl+D
 * // Or run:
 * >>> import sys
 * >>> sys.exit()
 *
 * //======= HARD reset is the same as performing a power cycle on the device =======
 * // Press reset switch or run:
 * >>> import machine
 * >>> machine.reset()
 *
 * //======= UPDATE LoPy4 Firmware using the *Pycom Firmware Update* application =======
 * // Download the application *Pycom Firmware Update* from <https://pycom.io/downloads/>;
 * // Plug LoPy4 + Expansion Board 2.0 to USB port;
 * //	- Before running Pycom Firmware Update, close any app (e.g. VSCode/Atom) that might be using USB port;
 * //	- Connect LoPy4 (with + Expansion Board 2.0) to USB port;
 * //	- Run Pycom Firmware Update:
 * //		- Uncheck boxes (Include development releases; Sendo anonymous error reports...)... Continue... Continue (twice)
 * //	- On Communication window choose Type: development... Continue
 * //		- On Pybytes activation token window... Skip
 * //		- On Advanced settings window choose File System: LittleFS and Check box: Erase during update... Continue
 *
 * ======== On the shell command line of localhost PC: ======== 
 * #STEP 1: start mosquitto:
 * $ /usr/local/sbin/mosquitto -v -p 1833
 * #Check if broker is running:
 * $ ps -ef | grep mosquitto
 *
 * #STEP 2: run a subscriber for some topic (-d for debug):
 * $ mosquitto_sub -p 1833 -h localhost -t lopy4rmoreira/sensor1 -d
 *
 * #STEP 3: run publisher to some topic (-d for debug):
 * $ mosquitto_pub -p 1833 -h localhost -t lopy4rmoreira/sensor1 -m "18" -d
 * 
 * #STEP 4: use lopy4 client to send/receive message to topic lopy4rmoreira/sensor1
 * ======== ======== ======== ======== ======== ======== ======== 
 * 
 """
 
 # =========================================== Define Functions Begin ===========================================
def settimeout(duration):
   pass

def get_data_from_sensor(sensor_id="RAND"):
    if sensor_id == "RAND":
        return ufun.random_in_range()

def sub_cb(topic, msg): 
   print('sub_cb(): received on topic = {} the msg = {}'.format(topic.decode(), msg.decode()))

def import_wifi_confs(file='./sys/wificonfs.json'):
    print("import_wifi_properties(): open file = {}".format(file))
    file = open(file, "r")
    wificonfs = ujson.load(file)
    print("import_wifi_properties(): got confs in file = {}".format(wificonfs))
    '''
    print("\n")
    wificonfs_str = ujson.dumps(wificonfs)
    print("import_wifi_properties(): all confs in file idented ="+wificonfs_str)
    print("\n")
    '''
    return wificonfs

def get_wifi_conf(wificonfs, ssid='eduroam'):
    print("get_wifi_conf(): get conf for ssid = {}".format(ssid))
    wifi_conf = wificonfs.get(ssid, 'NO_CONFIG')
    print("get_wifi_conf(): got wifi_conf = {}".format(wifi_conf))
    if wifi_conf!='NO_CONFIG':
        print("get_wifi_conf(): ssid {} -> {}\n".format(ssid, wifi_conf))
        netsec = wifi_conf.get('netsec', 'NA')
        print("get_wifi_conf(): {} = {}".format('netsec', WiFiClient.netsec_name_to_netsec(netsec)))
        print("get_wifi_conf(): {} = {}".format('brokerip', wifi_conf.get('brokerip', 'NA')))
        return (ssid, wifi_conf)
    return ('NO_SSID', 'NO_CONFIG')

def scan_wifi_net_configs(file='./sys/wificonfs.json'):
    print("scan_wifi_net_configs(): going to import net confs...")
    wificonfs = import_wifi_confs(file=file)
    print("scan_wifi_net_configs(): going to scan networks...")
    # Scan for networks:
    nets = wlan.scan()
    for net in nets:
        print("scan_wifi_net_configs(): found net = {}".format(net.ssid))
        #Load wifi configs
        (netssid, wificonf) = get_wifi_conf(wificonfs, ssid=net.ssid)
        print("scan_wifi_net_configs(): got conf = ({}, {})".format(net.ssid, wificonf))
        if wificonf != 'NO_CONFIG':
            return (netssid, wificonf)
    return ('NO_SSID', 'NO_CONFIG')
# =========================================== Define Functions End ===========================================

# =========================================== main() begin ===========================================
### if __name__ == "__main__":
""" To stop the script, click onto the Pymakr terminal, and press ctrl-c on your keyboard. """ 
print("\n")
print("main(): begin PROJ_CMOV_RSC1...")
pycom.heartbeat(False)

# The WLAN network class boots in WLAN.AP mode: wlan = WLAN() 
# Can boot as STA(tion) to connect to an existing network
wlan = WLAN(mode=WLAN.STA)

#mqtt_broker_addr_or_ip = 'test.mosquitto.org'
mqtt_broker_addr_or_ip = 'localhost'
#WiFi Configs file
file = "./sys/wificonfs_pub.json"

# Get configs of known available wifi networks
(wifi_ssid, wifi_config) = scan_wifi_net_configs(file=file)
print('main(): detected wifi_ssid = {}'.format(wifi_ssid))
if wifi_ssid!="NO_SSID":
    #netsec = wifi_config.get('netsec', WLAN.WPA2)
    netsec_str=wifi_config.get('netsec', 'WPA2')
    netsec = WiFiClient.netsec_name_to_netsec(netsec_str)
    timeout = wifi_config.get('timeout', 5000)
    username = wifi_config.get('username', None)
    password = wifi_config.get('password', None)
    identity = wifi_config.get('identity', None)
    ca_certs = wifi_config.get('cacerts', None)
    keyfile = wifi_config.get('keyfile', None)
    certfile = wifi_config.get('certfile', None)
    mqtt_broker_addr_or_ip = wifi_config.get('brokerip', 'localhost')
    mqtt_broker_port = wifi_config.get('brokerport', '1883')
    print('main(): using wifi_config = ({}, {}, {}, {})...'.format(wifi_ssid, netsec_str, mqtt_broker_addr_or_ip, mqtt_broker_port))
    
    #WiFiClient(self, wlan_mode, ssid, netsec = WLAN.WPA2, timeout=5000, username=None, password=None, identity=None, ca_certs='/flash/cert/ca.pem', keyfile='/flash/cert/client.key', certfile='/flash/cert/client.crt')
    # Choose WPA2 or WPA2_ENT
    #wificlient = WiFiClient(wlan, wifi_ssid, netsec, timeout, username, password, identity, ca_certs, keyfile, certfile)
    wificlient = WiFiClient.create_with_wifi_config(wlan, wifi_ssid, wifi_config)
    try:
        print('main(): connecting to WiFi ssid = {}...'.format(wifi_ssid))
        wificlient.connect_to_wifi_network()
    except OSError:
        print('main(): cannot connect to wifi ssid = {}!!'.format(wifi_ssid))
        sys.exit()

# Create mqtt client
dev_id = 'lopy4proj2223'
mqtt_port = int(mqtt_broker_port) # 1883
# Connect to mqqt server
mqttclient = MQTTClient(dev_id, mqtt_broker_addr_or_ip, mqtt_port)
try:
    print('main(): connecting to MQTT broker addr = {}, port = {}...'.format(mqtt_broker_addr_or_ip, mqtt_port))
    ##Set a callback listening a topic
    mqttclient.set_callback(sub_cb)
    mqttclient.connect()
except OSError as err:
    print('main(): cannot connect to broker on addr:port = {}:{} with err = {}!!!\n'.format(mqtt_broker_addr_or_ip, mqtt_port, err))
    sys.exit()

print('main(): connected to broker on addr = {}, port = {}...'.format(mqtt_broker_addr_or_ip, mqtt_port))
# Define topic for sensor1 pub/sub
topic = dev_id+'/sensor1'
print('main(): subscribing topic = {}...'.format(topic))
# Subscribe topic
mqttclient.subscribe(topic=topic)

# Prepare pub/rcv messages
# numbermsg = 5
# print('main(): going to publish & receive {} messages to/from topic {}...'.format(numbermsg, topic))
# sensorcount=0
# while sensorcount<numbermsg:
#     sensorcount+=1 # Update sensorcount
#     msg_data = get_data_from_sensor() # Read sensor data
#     print('main(): going to publish to topic/msg = {}/{}'.format(topic, msg_data)) # Debug msg
#     mqttclient.publish(topic, str(msg_data)) # Publishing sensor data
#     time.sleep(2)
#     print('main(): goint to check message on topic={}...'.format(topic)) # Debug msg
#     mqttclient.check_msg() # Check messages to receive
#     time.sleep(2)

#### CODE GOES HERE (?)
# Get sensor data
# Publish message
# Receive message
# 
# Send to The Things Network

# Disconnect from broker
print("main(): closing connection to broker... bye! :)") 
mqttclient.disconnect()