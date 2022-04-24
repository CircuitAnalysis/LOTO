import sys
import time
from ctypes import *
import matplotlib.pyplot as plt

# load dll (32 bit?)
OBJdll = windll.LoadLibrary(r".\USBInterFace64.dll")

print(" --------------------------------------------------------------------------------------------------")

# 1. Set the current oscilloscope device number to 7 (OSCH02)
    # void __stdcall SpecifyDevIdx(int idx)
SpecifyDevIdx = OBJdll.SpecifyDevIdx
SpecifyDevIdx.argtypes = [c_int]
SpecifyDevIdx(c_int(7))
print("1. Set the current oscilloscope device number to 7 (OSCH02)!")

# 2. Turn on the device
    # unsigned long __stdcall DeviceOpen()
DeviceOpen = OBJdll.DeviceOpen
DeviceOpen.restype = c_ulong
OpenRes = DeviceOpen()

if OpenRes == 0:
    print("2. The oscilloscope device is connected successfully!")
else:
    print("2. Oscilloscope device connection failed!")
    sys.exit(0)

# 3. Get the first address of the data buffer
    # unsigned char* __stdcall GetBuffer4Wr(int index)
GetBuffer4Wr = OBJdll.GetBuffer4Wr
GetBuffer4Wr.argtypes = [c_int]
GetBuffer4Wr.restype = POINTER(c_ubyte)
g_pBuffer = GetBuffer4Wr(c_int(-1))

if 0  == g_pBuffer:
    print("GetBuffer Failed!")
    sys.exit(0)
else:
    print("3. Get the first address of the data buffer successfully")

# Variables that record IO control bits
g_CtrlByte0 = 0
g_CtrlByte1 = 0

# X: Between steps 3 and 4, initialize the hardware trigger, if there is a problem with the trigger, please comment out this method.
    # unsigned char __stdcall USBCtrlTrans(unsigned char Request, unsigned short Value, unsigned long outBufSize)
USBCtrlTrans = OBJdll.USBCtrlTrans
USBCtrlTrans.argtypes = [c_ubyte, c_ushort, c_ulong]
USBCtrlTrans.restype = c_ubyte

g_CtrlByte1 &= 0xdf
g_CtrlByte1 |= 0x00
USBCtrlTrans(c_ubyte(0x24), c_ushort(g_CtrlByte1), c_ulong(1))
# Set the trigger position at 50% of the buffer (middle position)
USBCtrlTrans(c_ubyte(0x18), c_ushort(0xff), c_ulong(1))
USBCtrlTrans(c_ubyte(0x17), c_ushort(0x7f), c_ulong(1))

print("X: Between steps 3 and 4, initialize the hardware trigger, if there is a problem with the trigger, please comment out this method")

# 4. Set the buffer used to be 128K bytes (64K bytes per channel)
    # void __stdcall SetInfo(double dataNumPerPixar, double CurrentFreq, unsigned char ChannelMask, int ZrroUniInt, unsigned int  bufferoffset, unsigned int  HWbufferSize)
SetInfo = OBJdll.SetInfo
SetInfo.argtypes = [c_double, c_double, c_ubyte, c_int, c_uint,  c_uint]
SetInfo(c_double(1),  c_double(0),  c_ubyte(0x11),  c_int(0),   c_uint(0),  c_uint(64 * 1024 * 2) )

print("4. Set the buffer used to be 128K bytes (64K bytes per channel)")

# 5. Set the oscilloscope sample rate 976Khz
    #unsigned char USBCtrlTrans( unsigned char Request,  unsigned short Value,  unsigned long outBufSize )
#USBCtrlTrans = OBJdll.USBCtrlTrans
#USBCtrlTrans.argtypes = [c_ubyte, c_ushort, c_ulong]
#USBCtrlTrans.restype = c_ubyte

g_CtrlByte0 &= 0xf0
g_CtrlByte0 |= 0x0c
Transres = USBCtrlTrans( c_ubyte(0x94),  c_ushort(g_CtrlByte0),  c_ulong(1))

if 0  == Transres:
    print("5. error")
    sys.exit(0)
else:
    print(("5. Set the oscilloscope sample rate 976Khz" ))


time.sleep(0.1)
# Turn on the B channel (if it is not turned on, the default chB may be a logic analyzer or off)
g_CtrlByte1 &= 0xfe
g_CtrlByte1 |= 0x01
USBCtrlTrans(c_ubyte(0x24),  c_ushort(g_CtrlByte1),  c_ulong(1))


time.sleep(0.1)
# 6. Set the channel input range

# chA The input range is set to：-5V ~ +5V
g_CtrlByte1 &= 0xF7
g_CtrlByte1 |= 0x08
USBCtrlTrans(c_ubyte(0x22),  c_ushort(0x02),  c_ulong(1))
USBCtrlTrans(c_ubyte(0x24),  c_ushort(g_CtrlByte1),  c_ulong(1))
print("6. Set the channel input range The chA input range is set to：-5V ~ +5V")
time.sleep(0.1)

# chB The input range is set to：-5V ~ +5V
g_CtrlByte1 &= 0xF9
g_CtrlByte1 |= 0x02
USBCtrlTrans(c_ubyte(0x23),  c_ushort(0x00),  c_ulong(1))
USBCtrlTrans(c_ubyte(0x24),  c_ushort(g_CtrlByte1),  c_ulong(1))
print("6. Set the channel input range chB input range is set to：-5V ~ +5V")


# 7. Set Channel AC-DC Coupling
g_CtrlByte0 &= 0xef # Set chA to DC coupling
g_CtrlByte0 |= 0x10 # Set chA to DC coupling
USBCtrlTrans(c_ubyte(0x94),  c_ushort(g_CtrlByte0),  c_ulong(1))
print("7. Set channel AC-DC coupling Set chA to DC coupling")
time.sleep(0.1)

g_CtrlByte1 &= 0xef # Set chB to DC coupling
g_CtrlByte1 |= 0x10 # Set chB to DC coupling
Transres = USBCtrlTrans(c_ubyte(0x24),  c_ushort(g_CtrlByte1),  c_ulong(1))
print("7. Set channel AC-DC coupling Set chB to DC coupling")

# 8. Set the current trigger mode to no trigger
USBCtrlTrans(c_ubyte(0xE7),  c_ushort(0x00),  c_ulong(1))
print("8. Set the current trigger mode to no trigger")

# 8. Rising edge, or set the LED green light off
USBCtrlTrans(c_ubyte(0xC5),  c_ushort(0x00),  c_ulong(1))
print("8. Rising edge, or set the LED green light off")

time.sleep(5)
# 9.Control the device to start AD acquisition
    # unsigned long __stdcall USBCtrlTransSimple(unsigned long Request)
USBCtrlTransSimple = OBJdll.USBCtrlTransSimple
USBCtrlTransSimple.argtypes = [c_ulong]
USBCtrlTransSimple.restype = c_ulong
USBCtrlTransSimple(c_ulong(0x33))
print("9. Control the device to start AD acquisition")

# Delay 200
time.sleep(0.200)
print("X: sleep 200ms waiting for collection.... ")

# 10. Query whether AD collection and storage are completed. If the collection and storage are completed, the return value is 33.
rFillUp = USBCtrlTransSimple(c_ulong(0x50))

if 33 != rFillUp:
    print("10. The buffer data is not full (query result)")
    sys.exit(0)
else:
    print(("10. The buffer data is full (query result)" ))


# 11. According to the set data amount (SetInfo function), get, transmit, get the collected data
    # unsigned long __stdcall AiReadBulkData(unsigned long SampleCount, unsigned int EventNum, unsigned long TimeOut, unsigned char* Buffer, unsigned char Flag, unsigned int First_PacketNum)
AiReadBulkData = OBJdll.AiReadBulkData
AiReadBulkData.argtypes = [c_ulong, c_uint, c_ulong, POINTER(c_ubyte), c_ubyte, c_uint]
AiReadBulkData.restype = c_ulong
rBulkRes = AiReadBulkData( c_ulong(64 * 1024 * 2) ,  c_uint(1),  c_ulong(2000) , g_pBuffer,  c_ubyte(0),  c_uint(0))

if 0  == rBulkRes:
    print("11. Transfer the acquired data successfully!")
else:
    print("11. Failed to transfer the acquired data!")
    sys.exit(0)

#  chA and chB data, 64K data volume per channel
M = 64 * 1024 
chADataArray = (c_ubyte*M)()
chBDataArray = (c_ubyte*M)()
chADataArrayScaled = []
chBDataArrayScaled = []
timeDataArray = []

for i in range(0, M):
    chADataArray[i] = g_pBuffer[i * 2]
    chBDataArray[i] = g_pBuffer[i * 2 + 1]
    timeDataArray.append(i/976000) #oscilloscope sample rate 976Khz
    # 0-255 on the ADC give -5V to 5V on the scope:
    chADataArrayScaled.append(10 * (chADataArray[i] - 128) / 256)
    chBDataArrayScaled.append(10 * (chBDataArray[i] - 128) / 256)

# Use MatPlotLib to plot the waveforms 
fig, ax = plt.subplots()

ax.set(xlabel='time (s)', ylabel='voltage (V)', title='Keysight U2701A')

ax.plot(timeDataArray, chADataArrayScaled)
ax.plot(timeDataArray, chBDataArrayScaled)

ax.grid()
plt.ylim([-5, 5])
plt.show()

# 12. Turn off the device
    # unsigned long __stdcall DeviceClose()
DeviceClose = OBJdll.DeviceClose
DeviceClose.restype = c_ulong
DeviceClose()

print("12. Turn off the device")