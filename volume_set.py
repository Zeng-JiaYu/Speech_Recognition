#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : volume_set.py
# @Software   : PyCharm
# @Description：音量设置类


import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class VolumeSet(tk.Toplevel):
    """
    音量设置窗口类
    """
    def __init__(self, record_wav, parent, title: str):
        """
        构造函数，进行初始化设置
        :param record_wav: 传入的录音类对象，用来对其参数进行修改
        :param parent: 父窗口句柄
        :param title: 窗口标题
        """
        tk.Toplevel.__init__(self, parent, width=90, height=60)
        self.geometry("300x200+%d+%d" % (parent.winfo_rootx() + 300, parent.winfo_rooty() + 100))
        self.title(title)
        self.resizable(height=False, width=False)
        self.grab_set()  # 设置模态
        # 属性
        self.__record_wav = record_wav
        self.__current_value = tk.StringVar()
        self.__new_value = tk.StringVar()

        # 标签
        blank_label = tk.Label(self, width=6)  # 占位，若想去掉占位代码而实现相同设计，可以通过添加多层frame来解决
        blank_label.grid(row=0, column=0)
        self.current_value_label = tk.Label(self, text="当前识别幅值：", foreground='red', background='LightYellow',
                                            relief=tk.GROOVE)
        self.current_value_label.grid(row=0, column=1, padx=0, pady=20)
        self.new_value_label = tk.Label(self, text="预设识别幅值：", foreground='red', background='LightYellow',
                                        relief=tk.GROOVE)
        self.new_value_label.grid(row=1, column=1, padx=0, pady=2)
        unit_label1 = tk.Label(self, text="dB", foreground='DeepSkyBlue', relief=tk.FLAT)
        unit_label1.grid(row=0, column=3, pady=20)
        unit_label2 = tk.Label(self, text="dB", foreground='DeepSkyBlue', relief=tk.FLAT)
        unit_label2.grid(row=1, column=3, pady=2)
        # 显示label和编辑entry
        self.current_value_show = tk.Label(self, width=8, textvariable=self.__current_value,
                                           foreground='red', background='LightYellow', relief=tk.GROOVE)
        self.current_value_show.grid(row=0, column=2, pady=20)
        self.new_value_text = tk.Entry(self, width=8, textvariable=self.__new_value)
        self.new_value_text.grid(row=1, column=2, pady=2)
        # 设置初值
        self.__current_value.set(str(self.__record_wav.get_recognize_volume()))
        self.__new_value.set(str(self.__record_wav.get_recognize_volume()))
        # 按钮
        self.__init_btn()
        # 提示
        msg = "提示：既可直接输入值（0~1000），也可以通过按钮调整！"
        self.__prompt_information = tk.Label(self, text=msg, widt=40, foreground='MediumBlue', relief=tk.FLAT)
        self.__prompt_information.grid(row=4, column=0, sticky=tk.EW, padx=5, ipadx=2, columnspan=8)

    def __init_btn(self):
        """
        初始化按钮方法
        """
        images = [ImageTk.PhotoImage(Image.open("image/add_volume.png")),
                  ImageTk.PhotoImage(Image.open("image/sub_volume.png"))]
        img_w_h = 33

        btn_frame = tk.Frame(self, relief=tk.FLAT)

        add_sub_frame = tk.Frame(btn_frame, relief=tk.FLAT)
        add_btn = tk.Button(add_sub_frame, image=images[0], width=img_w_h, height=img_w_h, relief=tk.FLAT,
                            command=self.__add_volume)
        add_btn.image = images[0]
        add_btn.grid(row=0, column=0, padx=20)
        sub_btn = tk.Button(add_sub_frame, image=images[1], width=img_w_h, height=img_w_h, relief=tk.FLAT,
                            command=self.__sub_volume)
        sub_btn.image = images[1]
        sub_btn.grid(row=0, column=1, padx=0)
        add_sub_frame.grid(row=0, column=0, padx=10, pady=5, columnspan=2)

        ok_cancel_frame = tk.Frame(btn_frame, relief=tk.RIDGE)
        ok_btn = tk.Button(ok_cancel_frame, text="确认", width=6, command=self.__ok_click, relief=tk.RAISED)
        ok_btn.grid(row=0, column=0, padx=15, columnspan=1)
        cancel_btn = tk.Button(ok_cancel_frame, text="取消", width=6, command=self.__cancel_click, relief=tk.RAISED)
        cancel_btn.grid(row=0, column=1, columnspan=1)
        ok_cancel_frame.grid(row=1, column=0, columnspan=2)

        btn_frame.grid(row=3, column=1, padx=15, pady=15, sticky=tk.W, columnspan=2)

    def __ok_click(self):
        """
        确认按钮响应事件，设置识别声音幅值
        """
        value = int(self.__new_value.get())
        if 0 <= value <= self.__record_wav.volume_max:
            self.__record_wav.set_recognize_volume(value)
            tk.messagebox.showinfo('提示', '设置成功！设置的值为' + str(value) + 'dB。')
            self.destroy()
        else:
            tk.messagebox.showerror('错误', "设置值应介于0~" + str(self.__record_wav.volume_max) + "dB")

    def __cancel_click(self):
        """
        取消按钮响应函数，关闭子窗口
        """
        self.destroy()

    def __add_volume(self):
        """
        增大识别声音幅值，最大不超过96dB
        """
        value = int(self.__new_value.get())
        self.__new_value.set(str(value + 1))
        if value + 1 > self.__record_wav.volume_max:
            self.__new_value.set(str(self.__record_wav.volume_max))

    def __sub_volume(self):
        """
        减小识别声音幅值，最小不小于0dB
        """
        value = int(self.__new_value.get())
        self.__new_value.set(str(value - 1))
        if value - 1 < 0:
            self.__new_value.set(str(0))