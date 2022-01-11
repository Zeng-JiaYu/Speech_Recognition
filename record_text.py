#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : record_text.py
# @Software   : PyCharm
# @Description：word文件记录类

import win32api
import win32con
import win32gui
import win32com.client
import os
import time
import tkinter
from tkinter import messagebox


class RecordText:
    """
    识别文本记录操作类
    """

    def __init__(self, callback):
        """
        构造函数，进行初始化
        :param callback: 回调函数，参数：choice、value
        """
        self.callback = callback
        self.file_type = "doc"
        try:
            self.__word_app = win32com.client.Dispatch("Word.Application")
        except Exception as e:
            self.file_type = "txt"

    def save_record_doc(self, file_name: str, save_type: str, record_text: str):
        """
        进行文件的写入操作，将文本通过输出流写入文件
        :param file_name: 用于写入的文件名
        :param save_type: 写入的文件类型，'a'：追加写入模式，'w'：清空并覆盖写入模式
        :param record_text: 写入的文本记录
        """
        file_name = file_name + "." + self.file_type
        if len(record_text) > 0:
            self.close_record_doc(file_name)  # 若文件已打开，先关闭
            self.callback("status", "正在写入文件")
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            record_text = "写入时间：" + current_time + "\n" + record_text[0:-1]  # [0:-1]去掉末尾带有的\n
            if self.file_type == "txt":
                record_text = "\n" + record_text
            f = open(file_name, save_type)  # 打开一个文件用于尾部追加写入数据，如果不存在该文件，则创建
            f.write(record_text)
            f.close()
            self.callback("log", "文件写入完成")
            self.callback("status", "系统准备就绪")

    def open_record_doc(self, file_name: str):
        """
        使用office的word应用程序，打开文件传入的doc文件
        :param file_name: 需要打开的文件名（绝对路径）
        """
        self.callback("status", "正在打开文件")
        file_name = file_name + "." + self.file_type
        flag = os.path.exists(file_name)
        if flag and not self.file_is_open(file_name):
            if self.file_type == "doc":
                self.__word_app = win32com.client.Dispatch("Word.Application")
                self.__word_app.Visible = True
                self.__word_app.Documents.Open(file_name)
            else:
                win32api.ShellExecute(0, 'open', 'notepad.exe', file_name, '', 1)
            self.callback("log", "文件已打开")
        self.callback("status", "系统准备就绪")

    def close_record_doc(self, file_name: str):
        """
        使用office的word应用程序，关闭文件传入的doc文件
        :param file_name: 需要关闭的文件名（绝对路径）
        """
        file_name = file_name + "." + self.file_type
        flag = os.path.exists(file_name)
        if flag:
            if self.file_type == "doc" and self.file_is_open(file_name):  # 判断是否需要关闭，避免空处理异常
                self.__word_app.Quit()
                time.sleep(1)
            else:
                file_txt_name = os.path.basename(file_name) + " - 记事本"
                handle = win32gui.FindWindow(None, file_txt_name)
                win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)  # 关闭窗口
            self.callback("log", "文件已关闭")

    def delete_record_doc(self, file_name: str):
        """
        删除文件
        :param file_name: 需要删除的文件的路径
        """
        file_name = file_name + "." + self.file_type
        msg = "确认要删除" + os.path.basename(file_name) + "吗？"
        flag = tkinter.messagebox.askokcancel('提示', msg)  # 确定/取消，返回值true/false
        if flag and os.path.exists(file_name):
            self.close_record_doc(file_name)  # 若文件已打开，先关闭
            os.remove(file_name)
            self.callback("log", "文件已删除")

    def file_is_open(self, file_path):
        """
        判断文件是否已经处于打开状态
        :param file_path: 需要判断的文件的路径
        :return: 文件已打开返回True，否则返回False
        """
        try:
            open(file_path, "a")  # 以追加写入方式打开进行测试，只读方式会导致文件无法关闭
            return False
        except Exception as e:
            if "[Errno 13] Permission denied" in str(e):
                self.callback("log", "文件已经处于打开状态")
                return True
            else:
                return False
