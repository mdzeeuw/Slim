import mosquitto

def on_connect(obj, rc):
    print("rc: "+str(rc))

def on_message(obj, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

def on_publish(obj, mid):
    print("mid: "+str(mid))

def on_subscribe(obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(obj, level, string):
    print(string)

mqttc = mosquitto.Mosquitto("python_sub")
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
#mqttc.on_log = on_log
#mqttc.ssl_set("mosquitto.org.crt")
mqttc.connect("test.mosquitto.org", 1883, 10)
mqttc.subscribe("$SYS/#", 0)
mqttc.subscribe("#", 0)


rc = 0
while rc == 0:
    rc = mqttc.loop()

print("rc: "+str(rc))