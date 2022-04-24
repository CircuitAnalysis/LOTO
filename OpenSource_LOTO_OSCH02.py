import sys
import time
import json
from ctypes import *

# 加载dll
OBJdll = windll.LoadLibrary("USBInterFace.dll")

print " --------------------------------------------------------------------------------------------------"

# 1. 设置当前示波器设备编号为7(OSCH02)
    # void __stdcall SpecifyDevIdx(int idx)
SpecifyDevIdx = OBJdll.SpecifyDevIdx
SpecifyDevIdx.argtypes = [c_int]
SpecifyDevIdx(c_int(7))
print json.dumps("1. 设置当前示波器设备编号为7(OSCH02)!", encoding='UTF-8', ensure_ascii=False)


# 2. 打开设备
    # unsigned long __stdcall DeviceOpen()
DeviceOpen = OBJdll.DeviceOpen
DeviceOpen.restype = c_ulong
OpenRes = DeviceOpen()

if OpenRes == 0:
    print json.dumps("2. 示波器设备连接 成功!", encoding='UTF-8', ensure_ascii=False)
else:
    print json.dumps("2. 示波器设备连接 失败!", encoding='UTF-8', ensure_ascii=False)
    sys.exit(0)

    
# 3. 获取数据缓冲区首地址
    # unsigned char* __stdcall GetBuffer4Wr(int index)
GetBuffer4Wr = OBJdll.GetBuffer4Wr
GetBuffer4Wr.argtypes = [c_int]
GetBuffer4Wr.restype = POINTER(c_ubyte)
g_pBuffer = GetBuffer4Wr(c_int(-1))

if 0  == g_pBuffer:
    print json.dumps("GetBuffer Failed!", encoding='UTF-8', ensure_ascii=False)
    sys.exit(0)
else:
    print json.dumps("3. 获取数据缓冲区首地址 成功", encoding='UTF-8', ensure_ascii=False)


 
# 记录IO控制位的变量
g_CtrlByte0 = 0
g_CtrlByte1 = 0


# X: 在步骤3和4之间，初始化硬件触发, 如果触发出问题, 请注释掉这个方法不调用.
    # unsigned char __stdcall USBCtrlTrans(unsigned char Request, unsigned short Value, unsigned long outBufSize)
USBCtrlTrans = OBJdll.USBCtrlTrans
USBCtrlTrans.argtypes = [c_ubyte, c_ushort, c_ulong]
USBCtrlTrans.restype = c_ubyte

g_CtrlByte1 &= 0xdf
g_CtrlByte1 |= 0x00
USBCtrlTrans(c_ubyte(0x24), c_ushort(g_CtrlByte1), c_ulong(1))
# 设置触发位置在缓冲区50%(中间位置)
USBCtrlTrans(c_ubyte(0x18), c_ushort(0xff), c_ulong(1))
USBCtrlTrans(c_ubyte(0x17), c_ushort(0x7f), c_ulong(1))

print json.dumps("X: 在步骤3和4之间，初始化硬件触发, 如果触发出问题, 请注释掉这个方法不调用", encoding='UTF-8', ensure_ascii=False)



# 4. 设置使用的缓冲区为128K字节, 即每个通道64K字节
    # void __stdcall SetInfo(double dataNumPerPixar, double CurrentFreq, unsigned char ChannelMask, int ZrroUniInt, unsigned int  bufferoffset, unsigned int  HWbufferSize)
SetInfo = OBJdll.SetInfo
SetInfo.argtypes = [c_double, c_double, c_ubyte, c_int, c_uint,  c_uint]
SetInfo(c_double(1),  c_double(0),  c_ubyte(0x11),  c_int(0),   c_uint(0),  c_uint(64 * 1024 * 2) )

print json.dumps("4. 设置使用的缓冲区为128K字节, 即每个通道64K字节", encoding='UTF-8', ensure_ascii=False)

  
# 5. 设置示波器采样率 976Khz
    #unsigned char USBCtrlTrans( unsigned char Request,  unsigned short Value,  unsigned long outBufSize )
#USBCtrlTrans = OBJdll.USBCtrlTrans
#USBCtrlTrans.argtypes = [c_ubyte, c_ushort, c_ulong]
#USBCtrlTrans.restype = c_ubyte

g_CtrlByte0 &= 0xf0
g_CtrlByte0 |= 0x0c
Transres = USBCtrlTrans( c_ubyte(0x94),  c_ushort(g_CtrlByte0),  c_ulong(1))

if 0  == Transres:
    print json.dumps("5. error", encoding='UTF-8', ensure_ascii=False)
    sys.exit(0)
else:
    print (json.dumps("5. 设置示波器采样率976Khz", encoding='UTF-8', ensure_ascii=False) )


time.sleep(0.1)
# 开启B通道(如果不开启的话, 可能默认chB是逻辑分析仪或者关闭状态)
g_CtrlByte1 &= 0xfe
g_CtrlByte1 |= 0x01
USBCtrlTrans(c_ubyte(0x24),  c_ushort(g_CtrlByte1),  c_ulong(1))


time.sleep(0.1)
# 6.设置通道输入量程

# chA 输入量程设置为：-5V ~ +5V
g_CtrlByte1 &= 0xF7
g_CtrlByte1 |= 0x08
USBCtrlTrans(c_ubyte(0x22),  c_ushort(0x02),  c_ulong(1))
USBCtrlTrans(c_ubyte(0x24),  c_ushort(g_CtrlByte1),  c_ulong(1))
print json.dumps("6. 设置通道输入量程 chA 输入量程设置为：-5V ~ +5V", encoding='UTF-8', ensure_ascii=False)
time.sleep(0.1)

# chB 输入量程设置为：-5V ~ +5V
g_CtrlByte1 &= 0xF9
g_CtrlByte1 |= 0x02
USBCtrlTrans(c_ubyte(0x23),  c_ushort(0x00),  c_ulong(1))
USBCtrlTrans(c_ubyte(0x24),  c_ushort(g_CtrlByte1),  c_ulong(1))
print json.dumps("6. 设置通道输入量程 chB 输入量程设置为：-5V ~ +5V", encoding='UTF-8', ensure_ascii=False)


# 7. 设置通道交直流耦合
g_CtrlByte0 &= 0xef # 设置chA为DC耦合
g_CtrlByte0 |= 0x10 # 设置chA为DC耦合
USBCtrlTrans(c_ubyte(0x94),  c_ushort(g_CtrlByte0),  c_ulong(1))
print json.dumps("7. 设置通道交直流耦合 设置chA为DC耦合", encoding='UTF-8', ensure_ascii=False)
time.sleep(0.1)

g_CtrlByte1 &= 0xef # 设置chB为DC耦合
g_CtrlByte1 |= 0x10 # 设置chB为DC耦合
Transres = USBCtrlTrans(c_ubyte(0x24),  c_ushort(g_CtrlByte1),  c_ulong(1))
print json.dumps("7. 设置通道交直流耦合 设置chB为DC耦合", encoding='UTF-8', ensure_ascii=False)

# 8. 设置当前触发模式为 无触发
USBCtrlTrans(c_ubyte(0xE7),  c_ushort(0x00),  c_ulong(1))
print json.dumps("8. 设置当前触发模式为 无触发", encoding='UTF-8', ensure_ascii=False)

# 8. 上升沿，或者设置LED绿色灯灭
USBCtrlTrans(c_ubyte(0xC5),  c_ushort(0x00),  c_ulong(1))
print json.dumps("8. 上升沿，或者设置LED绿色灯灭", encoding='UTF-8', ensure_ascii=False)

time.sleep(0.1)
# 9.控制设备开始AD采集
    # unsigned long __stdcall USBCtrlTransSimple(unsigned long Request)
USBCtrlTransSimple = OBJdll.USBCtrlTransSimple
USBCtrlTransSimple.argtypes = [c_ulong]
USBCtrlTransSimple.restype = c_ulong
USBCtrlTransSimple(c_ulong(0x33))
print json.dumps("9. 控制设备开始AD采集", encoding='UTF-8', ensure_ascii=False)

# 延迟200
time.sleep(0.200)
print json.dumps("X: sleep200ms 等待采集.... ", encoding='UTF-8', ensure_ascii=False)


# 10.查询是否AD采集和存储完，如果采集存储结束，返回值是33
rFillUp = USBCtrlTransSimple(c_ulong(0x50))

if 33 != rFillUp:
    print json.dumps("10. 缓冲区数据没有蓄满(查询结果)", encoding='UTF-8', ensure_ascii=False)
    sys.exit(0)
else:
    print (json.dumps("10. 缓冲区数据已经蓄满(查询结果)", encoding='UTF-8', ensure_ascii=False) )


# 11. 根据设置数据量(SetInfo函数), 获取 传输获取采集的数据
    # unsigned long __stdcall AiReadBulkData(unsigned long SampleCount, unsigned int EventNum, unsigned long TimeOut, unsigned char* Buffer, unsigned char Flag, unsigned int First_PacketNum)
AiReadBulkData = OBJdll.AiReadBulkData
AiReadBulkData.argtypes = [c_ulong, c_uint, c_ulong, POINTER(c_ubyte), c_ubyte, c_uint]
AiReadBulkData.restype = c_ulong
rBulkRes = AiReadBulkData( c_ulong(64 * 1024 * 2) ,  c_uint(1),  c_ulong(2000) , g_pBuffer,  c_ubyte(0),  c_uint(0))

if 0  == rBulkRes:
    print json.dumps("11. 传输获取采集的数据 成功!", encoding='UTF-8', ensure_ascii=False)
else:
    print json.dumps("11. 传输获取采集的数据 失败!", encoding='UTF-8', ensure_ascii=False)
    sys.exit(0)


#  chA 和 chB 数据, 每个通道64K数据量
M = 64 * 1024 
chADataArray = (c_ubyte*M)()
chBDataArray = (c_ubyte*M)()

for i in range(0, M):
    chADataArray[i] = g_pBuffer[i * 2]
    chBDataArray[i] = g_pBuffer[i * 2 + 1]


    
# 换行
print

print " --------------------------------------------------------------------------------------------------"
    
# chA 打印采集到的数据 ( 打印 100个 )
for idx in range(91,191):
     print " chA: " + str(chADataArray[idx]),
     if idx != 0 and idx % 10 == 0 :
         print

print
print " --------------------------------------------------------------------------------------------------"
print

# chB 打印采集到的数据 ( 打印 100个 )
for idx in range(91,191):
     print " chB: " + str(chBDataArray[idx]),
     if idx != 0 and idx % 10 == 0 :
         print

print
print " --------------------------------------------------------------------------------------------------"

# 换行
print

    
# 999. 关闭设备
    # unsigned long __stdcall DeviceClose()
DeviceClose = OBJdll.DeviceClose
DeviceClose.restype = c_ulong
DeviceClose()

print "999. 关闭设备"
print
print
print


    

