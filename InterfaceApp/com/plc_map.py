from com.Services.plc_com import plc_com

class plc_map(plc_com):
        def __init__(self, ip_address):
                super().__init__()
                self.client.connect(ip_address, 0, 1)
                
                if self.client.get_connected():
                        print("Connect successfully!")
                #Initial Write Variable
                self.initWriteVar()
 
        def initWriteVar(self):
                self.o_deltabit0_0 = 0 
                self.o_deltabit0_1 = 0 
                self.o_deltabit0_2 = 0 
                self.o_deltabit0_3 = 0 
                self.o_deltabit0_4 = 0 
                self.o_deltabit0_5 = 0 
                self.o_deltabit0_6 = 0 
                self.o_deltabit0_7 = 0 
                self.o_deltabit1_0 = 0 
                self.o_deltabit1_1 = 0 
                self.o_deltabit1_2 = 0 
                self.o_deltabit1_3 = 0 
                self.o_deltabit1_4 = 0 
                self.o_deltabit1_5 = 0 
                self.o_deltabit1_6 = 0 
                self.o_deltabit1_7 = 0 
                self.o_deltabit2_0 = 0 
                self.o_deltabit2_1 = 0 
                self.o_deltabit2_2 = 0 
                self.o_deltabit2_3 = 0 
                self.o_deltabit2_4 = 0 
                self.o_deltabit2_5 = 0 
                self.o_deltabit2_6 = 0 
                self.o_deltabit2_7 = 0 

                self.o_deltaData1  = 0 
                self.o_deltaData2  = 0 
                self.o_deltaData3  = 0 
                self.o_deltaData4  = 0 
                self.o_deltaData5  = 0 
                self.o_deltaData6  = 0 
                self.o_deltaData7  = 0 
                self.o_deltaData8  = 0 
                self.o_deltaData9  = 0 
                self.o_deltaData10 = 0 
                self.o_deltaData11 = 0 
                self.o_deltaData12 = 0 
                self.o_deltaData13 = 0 
                self.o_deltaData14 = 0 
                self.o_deltaData15 = 0 
                self.o_deltaData16 = 0 
                self.o_deltaData17 = 0 
                self.o_deltaData18 = 0 
                self.o_deltaData19 = 0 
                self.o_deltaData20 = 0 
                self.o_deltaData21  = 0 
                self.o_deltaData22  = 0 
                self.o_deltaData23  = 0 
                self.o_deltaData24  = 0 
                self.o_deltaData25  = 0 
                self.o_deltaData26  = 0 
                self.o_deltaData27  = 0 
                self.o_deltaData28  = 0 
                self.o_deltaData29  = 0 
                self.o_deltaData30  = 0 
                self.o_deltaData31  = 0 
                self.o_deltaData32  = 0 
                self.o_deltaData33  = 0 
                self.o_deltaData34  = 0 
                self.o_deltaData35  = 0 
                self.o_deltaData36  = 0 
                self.o_deltaData37  = 0 
                self.o_deltaData38  = 0 
                self.o_deltaData39  = 0 
                self.o_deltaData40  = 0  
        #initial PLC to PC data:
        def Read_data(self):
                self.read_data_array()
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
                self.i_deltabit1_7 = self.i_Bit[2][7]
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
        #initial PLC to PC data:
        def Write_data(self):
                self.o_Bit[0][0] = self.o_deltabit0_0
                self.o_Bit[0][1] = self.o_deltabit0_1
                self.o_Bit[0][2] = self.o_deltabit0_2
                self.o_Bit[0][3] = self.o_deltabit0_3
                self.o_Bit[0][4] = self.o_deltabit0_4
                self.o_Bit[0][5] = self.o_deltabit0_5
                self.o_Bit[0][6] = self.o_deltabit0_6
                self.o_Bit[0][7] = self.o_deltabit0_7
                self.o_Bit[1][0] = self.o_deltabit1_0
                self.o_Bit[1][1] = self.o_deltabit1_1
                self.o_Bit[1][2] = self.o_deltabit1_2
                self.o_Bit[1][3] = self.o_deltabit1_3
                self.o_Bit[1][4] = self.o_deltabit1_4
                self.o_Bit[1][5] = self.o_deltabit1_5
                self.o_Bit[1][6] = self.o_deltabit1_6
                self.o_Bit[2][7] = self.o_deltabit1_7
                self.o_Bit[2][0] = self.o_deltabit2_0
                self.o_Bit[2][1] = self.o_deltabit2_1
                self.o_Bit[2][2] = self.o_deltabit2_2
                self.o_Bit[2][3] = self.o_deltabit2_3
                self.o_Bit[2][4] = self.o_deltabit2_4
                self.o_Bit[2][5] = self.o_deltabit2_5
                self.o_Bit[2][6] = self.o_deltabit2_6
                self.o_Bit[2][7] = self.o_deltabit2_7

                self.o_Data[1] = self.o_deltaData1 
                self.o_Data[2] = self.o_deltaData2 
                self.o_Data[3] = self.o_deltaData3 
                self.o_Data[4] = self.o_deltaData4 
                self.o_Data[5] = self.o_deltaData5 
                self.o_Data[6] = self.o_deltaData6 
                self.o_Data[7] = self.o_deltaData7 
                self.o_Data[8] = self.o_deltaData8 
                self.o_Data[9] = self.o_deltaData9 
                self.o_Data[10] = self.o_deltaData10
                self.o_Data[11] = self.o_deltaData11
                self.o_Data[12] = self.o_deltaData12
                self.o_Data[13] = self.o_deltaData13
                self.o_Data[14] = self.o_deltaData14
                self.o_Data[15] = self.o_deltaData15
                self.o_Data[16] = self.o_deltaData16
                self.o_Data[17] = self.o_deltaData17
                self.o_Data[18] = self.o_deltaData18
                self.o_Data[19] = self.o_deltaData19
                self.o_Data[20] = self.o_deltaData20
                self.o_Data[21] = self.o_deltaData21
                self.o_Data[22] = self.o_deltaData22
                self.o_Data[23] = self.o_deltaData23
                self.o_Data[24] = self.o_deltaData24
                self.o_Data[25] = self.o_deltaData25
                self.o_Data[26] = self.o_deltaData26
                self.o_Data[27] = self.o_deltaData27
                self.o_Data[28] = self.o_deltaData28
                self.o_Data[29] = self.o_deltaData29
                self.o_Data[30] = self.o_deltaData30
                self.o_Data[31] = self.o_deltaData31
                self.o_Data[32] = self.o_deltaData32
                self.o_Data[33] = self.o_deltaData33
                self.o_Data[34] = self.o_deltaData34
                self.o_Data[35] = self.o_deltaData35
                self.o_Data[36] = self.o_deltaData36
                self.o_Data[37] = self.o_deltaData37
                self.o_Data[38] = self.o_deltaData38
                self.o_Data[39] = self.o_deltaData39
                self.o_Data[40] = self.o_deltaData40

                self.write_data_array()


