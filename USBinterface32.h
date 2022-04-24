
// Device's information structure, macros and interface function definition.
#ifndef _DEVICE_HEADER
#define _DEVICE_HEADER


#ifdef	__cplusplus
extern "C" {
#endif


// Windows Header Files:
#include <windows.h>
#include <winioctl.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <malloc.h>


//////////////////////////////////////////////////////////////////////////////////
unsigned char __stdcall USBCtrlTrans(unsigned char Request, unsigned short Value, unsigned long outBufSize);
unsigned long __stdcall DeviceOpen();
unsigned long __stdcall DeviceClose();
unsigned long __stdcall AiReadBulkData(unsigned long SampleCount, unsigned int EventNum, unsigned long TimeOut, unsigned char* Buffer, unsigned char Flag, unsigned int First_PacketNum);
unsigned long __stdcall EventCheck(long Timeout);
unsigned long __stdcall CLearBuffer(unsigned char objA , unsigned char objB, unsigned int Num);
void __stdcall SpecifyDevIdx(int idx);
unsigned long __stdcall USBCtrlTransSimple(unsigned long Request);
unsigned char* __stdcall GetBuffer4Wr(int index);
void __stdcall SetInfo(double dataNumPerPixar, double CurrentFreq, unsigned char ChannelMask, int ZrroUniInt, unsigned int  bufferoffset, unsigned int  HWbufferSize);
///////////////////////////////////////////////////////////////////////////////////



#ifdef __cplusplus
}
#endif

#endif // _DEVICE_HEADER