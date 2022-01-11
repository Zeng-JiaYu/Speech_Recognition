#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : record_wav.py
# @Software   : PyCharm
# @Description：wav音频记录类
import os
import wave
from pyaudio import PyAudio, paInt16
import numpy as np
import math


class RecordWav:
    """
    录制音频类
    """
    RUN = 1
    STOP = 2

    def __init__(self, callback):
        """
        构造函数，进行初始化
        :param callback: 回调函数，参数：choice('log''status')、value
        """
        self.__callback = callback

        self.__framerate = 16000  # 采样帧频率 16000
        self.__channels = 1  # 声道
        self.__samp_width = 2  # 采样宽度 1 or 2
        self.__NUM_SAMPLES = 2000  # pyaudio内置缓冲大小

        self.status = self.STOP  # 录音状态，RUN表示可以进行录音
        self.__recognize_volume = 55   # 识别声音幅值，初始值设为55dB，为一般室内噪声值
        self.volume_max = 96  # 96dB为识别声音最大值，65535为16位的wav音频所能表示的最大值

    def __save_wave(self, filename, data):
        """
        将录制数据写入所给路径文件并保存wav文件
        :param filename: 录音所存放的路径
        :param data: 录制的数据
        """
        self.__callback("status", "正在保存录音文件")
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.__channels)
        wf.setsampwidth(self.__samp_width)
        wf.setframerate(self.__framerate)
        wf.writeframes(b"".join(data))
        wf.close()
        self.__callback("log", "录音文件保存成功")
        if self.status == self.STOP:
            self.__callback("status", "识别结束")
            self.__callback("status", "系统准备就绪")

    def record(self, filename: str) -> bool:
        """
        只录制单条语句，如果录制中途停止，则录制失败
        :param filename: 录音所存放的路径
        :return: 录音是否成功
        """
        pa = PyAudio()
        stream = pa.open(format=paInt16, channels=1, rate=self.__framerate, input=True,
                         frames_per_buffer=self.__NUM_SAMPLES)  # format=paInt16,以16进制格式存储音波幅值
        my_buf = []
        data_max = 0
        data = b""
        critical_volume = math.pow(10, self.__recognize_volume / 20)    # 临界音量
        while data_max < critical_volume:     # 录音机监测中
            data = stream.read(self.__NUM_SAMPLES)
            data = np.fromstring(data, dtype=np.short)
            data_max = np.max(data)
            if self.status == self.STOP:
                self.__callback("status", "识别结束")
                self.__callback("status", "系统准备就绪")
                break

        if self.status == self.RUN:
            self.__callback("status", "正在进行录音")
            while data_max > critical_volume - 100 and self.status == self.RUN:
                my_buf.append(data)
                data = stream.read(self.__NUM_SAMPLES)
                data = np.fromstring(data, dtype=np.short)
                data_max = np.max(data)
                print(".", end="")
            print()
            stream.close()
            self.__callback("log", "录音完成")
            self.__save_wave(filename, my_buf)
            self.status = self.STOP
        return os.path.exists(filename)

    def get_recognize_volume(self):
        """
        获取识别声音幅值
        :return: 返回识别声音幅值
        """
        return self.__recognize_volume

    def set_recognize_volume(self, value):
        """
        设置识别声音幅值
        :param value: 设置的值
        """
        self.__recognize_volume = value
