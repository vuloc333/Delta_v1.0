import snap7
from snap7.util import get_bool, get_int, set_bool, set_int
import numpy as np

class plc_com():
    def __init__(self):

        self.client = snap7.client.Client()
        self.client.connect("192.168.1.60", 0, 1)

        self.read_db_number =  int(2)
        self.write_db_number = int(1)

        #Initial data to write

        self.dbLength = int(42)
        self.byteofBit = int(3)
        self.byteofData = int(20)
        self.startData = int(0)

        if (self.byteofBit % 2) != 0:
            self.startData = self.byteofBit + 1
        else:
            self.startData = self.byteofBit

        self.i_Bit = np.zeros((self.byteofBit,8), dtype = bool)
        self.i_Data = np.zeros((self.byteofData + 1), dtype = int)
        
        self.o_Bit = np.zeros((self.byteofBit,8), dtype = bool)
        self.o_Data = np.zeros((self.byteofData + 1), dtype = int)

        if self.client.get_connected():
            print("Connect successfully!")
    
    def read_data_array(self):

        self.data_read = self.client.db_read(self.read_db_number, 0, self.dbLength)

        for i in range(self.byteofBit):
            for j in range (8):
                self.i_Bit[i][j] = get_bool(self.data_read, i, j)

        for i in range(self.startData, self.dbLength - 1, 2):
            numarr = (i - self.startData) / 2 + 1
            numarr = int(numarr)
            self.i_Data[numarr] = get_int(self.data_read, i) 


    def write_data_array(self):

        WriteData = bytearray(self.dbLength)
        for i in range (self.byteofBit):
            for j in range (8):
                snap7.util.set_bool(WriteData, i, j, self.o_Bit[i, j])

        for i in range(self.startData, self.byteofData - 1, 2):
            numarr = (i - self.startData) / 2 + 1
            numarr = int(numarr)
            snap7.util.set_int(WriteData, i, self.o_Data[numarr])
        
        self.client.db_write(self.write_db_number, 0, WriteData)

        
        