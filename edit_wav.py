#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : edit_wav.py
# @Software   : PyCharm
# @Description：音频播放类

import os
import wave

from ffmpy import FFmpeg
from pyaudio import PyAudio
import math
import shutil
import tkinter as tk
from tkinter import messagebox
from file_dialog import FileDialog


class EditWav:
    """
    音频播放类
    """
    RUN = 1
    PAUSE = 2
    STOP = 3

    def __init__(self, callback):
        """
        构造函数，进行初始化
        :param callback: 回调函数，1.参数：choice("progressbar"：更新进度条，"begin_flag"：设置begin_flag)、value
                                2.参数：choice（”status“”log“）、value
        """
        self.__callback = callback  # 回调函数
        self.play_status = self.STOP  # 播放状态（播放/暂停/终止）

    def play_wav(self, filename):
        """
        播放传入路径的音频文件
        :param filename: 音频文件的绝对路径
        """
        if self.play_status == self.RUN:
            wf = wave.open(filename, 'rb')  # 从目录中读取语音
            sum_frame = wf.getparams().nframes  # 音频总帧数
            chunk = 1024  # 按照1024的块读取音频数据到音频流
            p = PyAudio()  # 创建播放器
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),
                            rate=wf.getframerate(), frames_per_buffer=chunk, output=True)  # 打开音频流，output=True为音频输出
            # 按照1024的块读取音频数据到音频流，并播放
            count = 0
            data = wf.readframes(chunk)  # 读取数据
            while len(data) > 0 and self.play_status != self.STOP:
                if self.play_status == self.RUN:
                    count += 1
                    var = math.floor(100 * count * chunk / sum_frame)
                    self.__callback("progressbar", var)  # 更新进度条的值
                    stream.write(data)
                    data = wf.readframes(chunk)
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.__callback("progressbar", 0)  # 更新进度条的值
        # 恢复状态
        self.__callback("begin_flag", False)
        self.play_status = self.STOP

    def format_to_wav(self, file_path):
        """
        将外部导入的other格式文件转化为‘pcm-16位 int、1通道、16000Hz采样率的wav文件'
        :param file_path: 外部音频文件存放的路径
        :return: 返回格式转换后的文件名绝对路径，返回空表示转换失败
        """
        self.__callback("log", "音频格式转换为wav")
        path_out = os.path.splitext(file_path)[0] + ".wav"
        ff = FFmpeg(
            inputs={file_path: None},
            outputs={path_out: ['-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000']}
        )
        ff.run()
        if os.path.exists(path_out):
            return path_out
        return ""

    def merge_wav(self, read_path, merge_path, init_window_name):
        """
        合并音频记录文件
        :param read_path:
        :param merge_path:
        :param init_window_name:
        :return:
        """
        self.__callback("status", "正在进行音频记录文件的合并")
        self.__callback("log", "合并音频记录wav文件")
        wav_list = []
        if os.path.exists(read_path):
            for wav_file in os.listdir(read_path):  # 抽取音频记录所在文件夹下所有wav文件的绝对路径
                if wav_file.endswith('.wav'):
                    wav_list.append(wav_file)
        if len(wav_list) > 0:
            data = []
            for wav_file in wav_list:
                wav_file = read_path + wav_file
                w = wave.open(wav_file, 'rb')
                data.append([w.getparams(), w.readframes(w.getnframes())])  # 获取音频文件的各项参数、音频数据
                w.close()
            output = wave.open(merge_path, 'wb')
            output.setparams(data[0][0])  # 将读取的第一个文件的参数设置为合并文件的参数
            for index in range(len(data)):  # 将数据写入合并文件
                output.writeframes(data[index][1])
            output.close()
            if os.path.exists(merge_path):
                self.__callback("log", "合并成功")
                msg = "合并完成，共合并" + str(len(wav_list)) + "条音频文件。\n合并文件保存路径为：" + merge_path + "，您是否要修改路径"
                flag = tk.messagebox.askyesno('提示', msg)  # 是/否，返回值true/false
                if flag:
                    file_dialog = FileDialog(init_window_name, "保存合并音频记录", ".wav")
                    new_file_path = file_dialog.get_save_file_name()
                    if len(new_file_path) > 0:
                        shutil.move(merge_path, new_file_path)  # 移动文件
                        if os.path.exists(new_file_path):
                            self.__callback("log", "合并文件路径修改成功")
                            tk.messagebox.showinfo('提示', '路径修改成功！')
                        else:
                            self.__callback("log", "合并文件路径修改失败")
                            tk.messagebox.showerror('错误', '操作失败！')
            else:
                tk.messagebox.showerror('错误', '操作失败！')
        else:
            tk.messagebox.showinfo('提示', '合并失败，没有可用于合并的音频记录！')
            self.__callback("log", "合并失败")
        self.__callback("status", "系统准备就绪")
