import snap7
from snap7.util import get_bool, get_int, set_bool, set_int
import numpy as np
from typing import Any, Optional


class plc_map:
    def __init__(self, ip_address: str) -> None:
        super().__init__()
        self.client: snap7.client.Client = snap7.client.Client()
        self.read_db_number = 2
        self.write_db_number = 1
        self.dbLength = 82
        self.byteofBit = 4
        self.byteofData = 40
        self.startData = 4

        self.i_Bit = np.zeros((self.byteofBit, 8), dtype=bool)
        self.i_Data = np.zeros((self.byteofData + 1), dtype=int)
        self.o_Bit = np.zeros((self.byteofBit, 8), dtype=bool)
        self.o_Data = np.zeros((self.byteofData + 1), dtype=int)

        self.initWriteVar()
        self.connect(ip_address)

    def connect(self, ip_address: str) -> None:
        try:
            self.client.connect(ip_address, 0, 1)
        except Exception as exc:
            raise ConnectionError(f"PLC connect failed: {exc}")
        print("Connect successfully!")
        
    def disconnect(self) -> None:
        try:
            self.client.disconnect()
        except Exception:
            pass

    def Read_data(self) -> None:
        try:
            self.client.get_connected()
        except Exception:
            return

        data_read = self.client.db_read(self.read_db_number, 0, self.dbLength)
        self._decode_input_bits(data_read)
        self._decode_input_data(data_read)
        self.MakeReadArray()

    def Write_data(self) -> None:
        try:
            self.client.get_connected()
        except Exception:
            return

        self.MakeWriteArray()
        write_data = bytearray(self.dbLength)

        for i in range(self.byteofBit):
            for j in range(8):
                set_bool(write_data, i, j, bool(self.o_Bit[i, j]))

        for i in range(self.startData, self.dbLength - 1, 2):
            numarr = (i - self.startData) // 2 + 1
            if 0 <= numarr < len(self.o_Data):
                set_int(write_data, i, int(self.o_Data[numarr]))

        self.client.db_write(self.write_db_number, 0, write_data)

    def initWriteVar(self) -> None:
        # Bit outputs
        self.o_Arm1JogFw = 0
        self.o_Arm1JogBw = 0
        self.o_Arm1Home = 0
        self.o_deltabit0_3 = 0
        self.o_deltabit0_4 = 0
        self.o_deltabit0_5 = 0
        self.o_deltabit0_6 = 0
        self.o_deltabit0_7 = 0
        self.o_Arm2JogFw = 0
        self.o_Arm2JogBw = 0
        self.o_Arm2Home = 0
        self.o_deltabit1_3 = 0
        self.o_deltabit1_4 = 0
        self.o_deltabit1_5 = 0
        self.o_deltabit1_6 = 0
        self.o_deltabit1_7 = 0
        self.o_Arm3JogFw = 0
        self.o_Arm3JogBw = 0
        self.o_Arm3Home = 0
        self.o_deltabit2_3 = 0
        self.o_deltabit2_4 = 0
        self.o_deltabit2_5 = 0
        self.o_deltabit2_6 = 0
        self.o_deltabit2_7 = 0
        self.o_AllHome = 0
        self.o_AllMove = 0
        self.o_deltabit3_2 = 0
        self.o_deltabit3_3 = 0
        self.o_deltabit3_4 = 0
        self.o_deltabit3_5 = 0
        self.o_deltabit3_6 = 0
        self.o_deltabit3_7 = 0

        # Data outputs
        self.o_arm1RunSpeed = 0
        self.o_arm1Ramp = 0
        self.o_arm1JogSpeed = 0
        self.o_arm1gear = 0
        self.o_arm1MicroStep = 0
        self.o_xTestPos = 0
        self.o_yTestPos = 0
        self.o_zTestPos = 0
        self.o_deltaData9 = 0
        self.o_deltaData10 = 0
        self.o_arm2RunSpeed = 0
        self.o_arm2Ramp = 0
        self.o_arm2JogSpeed = 0
        self.o_arm2gear = 0
        self.o_arm2MicroStep = 0
        self.o_deltaData16 = 0
        self.o_RadiusBase = 0
        self.o_RadiusEE = -1
        self.o_BicepLength = -1
        self.o_ForeArmLength = -1
        self.o_arm3RunSpeed = -1
        self.o_arm3Ramp = -1
        self.o_arm3JogSpeed = -1
        self.o_arm3gear = -1
        self.o_arm3MicroStep = -1
        self.o_deltaData26 = -1
        self.o_deltaData27 = -1
        self.o_deltaData28 = -1
        self.o_deltaData29 = -1
        self.o_deltaData30 = -1
        self.o_ConvRunSpeed = -1
        self.o_ConvRamp = -1
        self.o_deltaData33 = -1
        self.o_deltaData34 = -1
        self.o_zPrePick = -1
        self.o_zClass = -1
        self.o_zPitchClass = -1
        self.o_yPitchClass = -1
        self.o_xClass1 = -1
        self.o_yClass1 = -1

    def _decode_input_bits(self, data_read: bytes) -> None:
        for i in range(self.byteofBit):
            for j in range(8):
                self.i_Bit[i][j] = get_bool(data_read, i, j)

    def _decode_input_data(self, data_read: bytes) -> None:
        for i in range(self.startData, self.dbLength - 1, 2):
            numarr = (i - self.startData) // 2 + 1
            if 0 <= numarr < len(self.i_Data):
                self.i_Data[numarr] = get_int(data_read, i)

    def MakeReadArray(self) -> None:
        self.i_deltabit0_0 = self.i_Bit[0][0]
        self.i_deltabit0_1 = self.i_Bit[0][1]
        self.i_deltabit0_2 = self.i_Bit[0][2]
        self.i_deltabit0_3 = self.i_Bit[0][3]
        self.i_deltabit0_4 = self.i_Bit[0][4]
        self.i_deltabit0_5 = self.i_Bit[0][5]
        self.i_deltabit0_6 = self.i_Bit[0][6]
        self.i_deltabit0_7 = self.i_Bit[0][7]
        self.i_deltabit1_0 = self.i_Bit[1][0]
        self.i_deltabit1_1 = self.i_Bit[1][1]
        self.i_deltabit1_2 = self.i_Bit[1][2]
        self.i_deltabit1_3 = self.i_Bit[1][3]
        self.i_deltabit1_4 = self.i_Bit[1][4]
        self.i_deltabit1_5 = self.i_Bit[1][5]
        self.i_deltabit1_6 = self.i_Bit[1][6]
        self.i_deltabit1_7 = self.i_Bit[1][7]
        self.i_deltabit2_0 = self.i_Bit[2][0]
        self.i_deltabit2_1 = self.i_Bit[2][1]
        self.i_deltabit2_2 = self.i_Bit[2][2]
        self.i_deltabit2_3 = self.i_Bit[2][3]
        self.i_deltabit2_4 = self.i_Bit[2][4]
        self.i_deltabit2_5 = self.i_Bit[2][5]
        self.i_deltabit2_6 = self.i_Bit[2][6]
        self.i_deltabit2_7 = self.i_Bit[2][7]

        self.i_deltaData1 = self.i_Data[1]
        self.i_deltaData2 = self.i_Data[2]
        self.i_deltaData3 = self.i_Data[3]
        self.i_deltaData4 = self.i_Data[4]
        self.i_deltaData5 = self.i_Data[5]
        self.i_deltaData6 = self.i_Data[6]
        self.i_deltaData7 = self.i_Data[7]
        self.i_deltaData8 = self.i_Data[8]
        self.i_deltaData9 = self.i_Data[9]
        self.i_deltaData10 = self.i_Data[10]
        self.i_deltaData11 = self.i_Data[11]
        self.i_deltaData12 = self.i_Data[12]
        self.i_deltaData13 = self.i_Data[13]
        self.i_deltaData14 = self.i_Data[14]
        self.i_deltaData15 = self.i_Data[15]
        self.i_deltaData16 = self.i_Data[16]
        self.i_deltaData17 = self.i_Data[17]
        self.i_deltaData18 = self.i_Data[18]
        self.i_deltaData19 = self.i_Data[19]
        self.i_deltaData20 = self.i_Data[20]
        self.i_deltaData21 = self.i_Data[21]
        self.i_deltaData22 = self.i_Data[22]
        self.i_deltaData23 = self.i_Data[23]
        self.i_deltaData24 = self.i_Data[24]
        self.i_deltaData25 = self.i_Data[25]
        self.i_deltaData26 = self.i_Data[26]
        self.i_deltaData27 = self.i_Data[27]
        self.i_deltaData28 = self.i_Data[28]
        self.i_deltaData29 = self.i_Data[29]
        self.i_deltaData30 = self.i_Data[30]
        self.i_deltaData31 = self.i_Data[31]
        self.i_deltaData32 = self.i_Data[32]
        self.i_deltaData33 = self.i_Data[33]
        self.i_deltaData34 = self.i_Data[34]
        self.i_deltaData35 = self.i_Data[35]
        self.i_deltaData36 = self.i_Data[36]
        self.i_deltaData37 = self.i_Data[37]
        self.i_deltaData38 = self.i_Data[38]
        self.i_deltaData39 = self.i_Data[39]
        self.i_deltaData40 = self.i_Data[40]

    def MakeWriteArray(self) -> None:
        self.o_Bit[0][0] = self.o_Arm1JogFw
        self.o_Bit[0][1] = self.o_Arm1JogBw
        self.o_Bit[0][2] = self.o_Arm1Home
        self.o_Bit[0][3] = self.o_deltabit0_3
        self.o_Bit[0][4] = self.o_deltabit0_4
        self.o_Bit[0][5] = self.o_deltabit0_5
        self.o_Bit[0][6] = self.o_deltabit0_6
        self.o_Bit[0][7] = self.o_deltabit0_7

        self.o_Bit[1][0] = self.o_Arm2JogFw
        self.o_Bit[1][1] = self.o_Arm2JogBw
        self.o_Bit[1][2] = self.o_Arm2Home
        self.o_Bit[1][3] = self.o_deltabit1_3
        self.o_Bit[1][4] = self.o_deltabit1_4
        self.o_Bit[1][5] = self.o_deltabit1_5
        self.o_Bit[1][6] = self.o_deltabit1_6
        self.o_Bit[1][7] = self.o_deltabit1_7

        self.o_Bit[2][0] = self.o_Arm3JogFw
        self.o_Bit[2][1] = self.o_Arm3JogBw
        self.o_Bit[2][2] = self.o_Arm3Home
        self.o_Bit[2][3] = self.o_deltabit2_3
        self.o_Bit[2][4] = self.o_deltabit2_4
        self.o_Bit[2][5] = self.o_deltabit2_5
        self.o_Bit[2][6] = self.o_deltabit2_6
        self.o_Bit[2][7] = self.o_deltabit2_7

        self.o_Bit[3][0] = self.o_AllHome
        self.o_Bit[3][1] = self.o_AllMove
        self.o_Bit[3][2] = self.o_deltabit3_2
        self.o_Bit[3][3] = self.o_deltabit3_3
        self.o_Bit[3][4] = self.o_deltabit3_4
        self.o_Bit[3][5] = self.o_deltabit3_5
        self.o_Bit[3][6] = self.o_deltabit3_6
        self.o_Bit[3][7] = self.o_deltabit3_7

        self.o_Data[1] = self.o_arm1RunSpeed
        self.o_Data[2] = self.o_arm1Ramp
        self.o_Data[3] = self.o_arm1JogSpeed
        self.o_Data[4] = self.o_arm1gear
        self.o_Data[5] = self.o_arm1MicroStep
        self.o_Data[6] = self.o_xTestPos
        self.o_Data[7] = self.o_yTestPos
        self.o_Data[8] = self.o_zTestPos
        self.o_Data[9] = self.o_deltaData9
        self.o_Data[10] = self.o_deltaData10

        self.o_Data[11] = self.o_arm2RunSpeed
        self.o_Data[12] = self.o_arm2Ramp
        self.o_Data[13] = self.o_arm2JogSpeed
        self.o_Data[14] = self.o_arm2gear
        self.o_Data[15] = self.o_arm2MicroStep
        self.o_Data[16] = self.o_deltaData16
        self.o_Data[17] = self.o_RadiusBase
        self.o_Data[18] = self.o_RadiusEE
        self.o_Data[19] = self.o_BicepLength
        self.o_Data[20] = self.o_ForeArmLength

        self.o_Data[21] = self.o_arm3RunSpeed
        self.o_Data[22] = self.o_arm3Ramp
        self.o_Data[23] = self.o_arm3JogSpeed
        self.o_Data[24] = self.o_arm3gear
        self.o_Data[25] = self.o_arm3MicroStep
        self.o_Data[26] = self.o_deltaData26
        self.o_Data[27] = self.o_deltaData27
        self.o_Data[28] = self.o_deltaData28
        self.o_Data[29] = self.o_deltaData29
        self.o_Data[30] = self.o_deltaData30

        self.o_Data[31] = self.o_ConvRunSpeed
        self.o_Data[32] = self.o_ConvRamp
        self.o_Data[33] = self.o_deltaData33
        self.o_Data[34] = self.o_deltaData34
        self.o_Data[35] = self.o_zPrePick
        self.o_Data[36] = self.o_zClass
        self.o_Data[37] = self.o_zPitchClass
        self.o_Data[38] = self.o_yPitchClass
        self.o_Data[39] = self.o_xClass1
        self.o_Data[40] = self.o_yClass1
