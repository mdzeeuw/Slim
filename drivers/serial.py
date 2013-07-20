import driver
import common.config
import common.error

import serial


class SerialGateway(driver.Driver):

    def initialize(self, init_mqtt=True, init_serial=True):
        try:
            # Get my config
            self.config = common.config.Config("serial")

            if init_mqtt:
                self.client = common.mqtt.MQTTClient(self.config.get("client_id", "SerialGateway"))

                self.client.connect()

            if init_serial:
                self.serial_conn = serial.Serial(self.config.get("port", "/dev/ttyUSB0"), self.config.get("speed", 57600))

                # Clear the current buffers
                self.serial_conn.flushInput()

                self.serial_conn.flushOutput()

            #date = datetime.datetime.utcnow()
            #self.data_log = open('logs/ser-{0}.txt'.format(datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")), 'w')
        except Exception as e:
            self.s_conn = False
            self.logger.error(e)
            time.sleep(2)

        except Exception:
            return False

        return True

if __name__ == '__main__':
    gw = SerialGateway()

    gw.start()
