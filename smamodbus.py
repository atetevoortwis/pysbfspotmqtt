from pymodbus.client.sync import ModbusTcpClient
import logging
import struct
modbus_fields = {
    'EToday': {'address': 30535, 'datatype': 'U32', 'scale': 1000, 'unit': 'kWh'},
    'ETotal': {'address': 30529, 'datatype': 'U32', 'scale': 1000, 'unit': 'kWh'},
    'String1DCPower': {'address': 30773, 'datatype': 'S32', 'scale': 1, 'unit': 'kWh'},
    'String1DCVoltage': {'address': 30771, 'datatype': 'S32', 'scale': 100, 'unit': 'V'},
    'String1DCCurrent': {'address': 30769, 'datatype': 'S32', 'scale': 1000, 'unit': 'A'},
    'String2DCPower': {'address': 30961, 'datatype': 'S32', 'scale': 1, 'unit': 'kW'},
    'String2DCVoltage': {'address': 30959, 'datatype': 'S32', 'scale': 100, 'unit': 'V'},
    'String2DCCurrent': {'address': 30957, 'datatype': 'S32', 'scale': 1000, 'unit': 'A'},
    'Phase1ACPower': {'address': 30775, 'datatype': 'U32', 'scale': 1, 'unit': 'kW'},
    'Phase1ACVoltage': {'address': 30783, 'datatype': 'U32', 'scale': 100, 'unit': 'V'},
    'Phase1ACCurrent': {'address': 30977, 'datatype': 'S32', 'scale': 1000, 'unit': 'A'},
    'InternalTemp1': {'address': 30953, 'datatype': 'S32', 'scale': 10, 'unit': 'C'},
    'InternalTemp2': {'address': 34113, 'datatype': 'S32', 'scale': 10, 'unit': 'C'},
    'TempHeatsink': {'address': 34109, 'datatype': 'S32', 'scale': 10, 'unit': 'C'},
}

class SMAModbus:
    def __init__(self,url,unit_id):
        logging.info('Connecting to Modbus server: {}'.format(url))
        self._client = ModbusTcpClient('192.168.1.88')
        self._client.connect()
        logging.info('Connected')
        self._unit_id = unit_id


    def readModbus(self):
        if not self._client.is_socket_open():
            self._client.connect()
        data = {}
        for tag,cfg in modbus_fields.items():
            result = self._client.read_holding_registers(cfg['address'], 2, unit=self._unit_id)
            w1 = struct.pack('H', result.registers[0]) # Assuming register values are unsigned short's
            w2 = struct.pack('H', result.registers[1]) # Assuming register values are unsigned short's
            if cfg['datatype'] == 'S32':
                v = struct.unpack('i', w2 + w1)
            elif cfg['datatype'] == 'U32':
                v = struct.unpack('I', w2 + w1)
            else:
                raise NotImplementedError('Datatype {} is not implemented'.format(cfg['datatype']))
            v = v[0]/cfg['scale']
            v =  (result.registers[0]*2**16+result.registers[1])/cfg['scale']
            # check for negative or larger than 100y of output
            if v<0 or v>100*3000*1000:
                v=0.
            data[tag] = v
        return data
