#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : interview_set.py
# @Software   : PyCharm
# @Description：约谈设置窗口

import pypinyin
import tkinter as tk
from tkinter import messagebox
import os


class InterviewSet(tk.Toplevel):
    """
    识别个体设置窗口类
    """
    def __init__(self, callback, parent, title: str, file_path_name):
        """
        构造函数，进行初始化设置
        :param callback: 回调函数，传入参数name为识别人姓名的拼音
        :param parent: 父窗口句柄
        :param title: 窗口标题
        :param file_path_name: 用来生成个体文件夹的初始目录名
        """
        tk.Toplevel.__init__(self, parent, width=90, height=60)
        self.geometry("300x200+%d+%d" % (parent.winfo_rootx() + 300, parent.winfo_rooty() + 100))
        self.title(title)
        self.resizable(height=False, width=False)
        self.grab_set()  # 设置模态
        # 属性
        self.__callback = callback
        self.__file_path_name = file_path_name  # 传入路径为 .../record
        self.__name_pinyin = tk.StringVar()

        # 标签
        blank_label = tk.Label(self, width=6)
        blank_label.grid(row=0, column=0)
        self.interview_name_label = tk.Label(self, text="姓名：", foreground='red', background='LightYellow',
                                             relief=tk.GROOVE)
        self.interview_name_label.grid(row=0, column=1, padx=0, pady=20)
        self.interview_pinyin_label = tk.Label(self, text="拼音：", foreground='red', background='LightYellow',
                                               relief=tk.GROOVE)
        self.interview_pinyin_label.grid(row=1, column=1, padx=0, pady=2)

        self.interview_name_text = tk.Entry(self, width=20, validate='key')
        self.interview_name_text.grid(row=0, column=2, pady=20)
        self.interview_name_text.bind("<Key>", self.__show_pinyin)  # 键盘输入触发事件
        self.interview_name_pinyin = tk.Label(self, width=20, textvariable=self.__name_pinyin, foreground='red',
                                              background='LightYellow', relief=tk.GROOVE)
        self.interview_name_pinyin.grid(row=1, column=2, pady=2)
        # 按钮
        ok_btn = tk.Button(self, text="确认", width=6, command=self.__ok_click, relief=tk.RAISED)
        ok_btn.grid(row=3, column=1, padx=10, pady=28, columnspan=2)

        # 提示
        msg = "提示：输入完成后请按回车键，最后单击确认按钮！"
        self.__prompt_information = tk.Label(self, text=msg, widt=40, foreground='MediumBlue', relief=tk.FLAT)
        self.__prompt_information.grid(row=4, column=0, sticky=tk.EW, padx=5, ipadx=2, columnspan=8)

    def __show_pinyin(self, event):
        """
        刷新显示拼音
        :param event: 鼠标事件
        """
        name_pinyin = str(pinyin(self.interview_name_text.get()))
        self.__name_pinyin.set(name_pinyin)

    def __ok_click(self):
        """
        确认按钮响应事件，设置识别个体的名称（姓名），创建个体数据存储目录
        """
        name = str(pinyin(self.interview_name_text.get()))
        self.__callback(name)  # 通过回调函数传递设置的识别人信息
        if not os.path.exists(self.__file_path_name + name):
            os.makedirs(self.__file_path_name + name + "/" + "wav/")
            os.makedirs(self.__file_path_name + name + "/" + "doc/")
        tk.messagebox.showinfo('提示', '设置成功！')
        self.destroy()


def pinyin(word):
    """
    生成不带声调的拼音(style=pypinyin.NORMAL)
    :param word: 需要操作的汉字
    :return: 返回汉字的拼音
    """
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s
