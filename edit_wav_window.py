#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : edit_wav_window.py
# @Software   : PyCharm
# @Description：模态子窗口类

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import os
import time

from edit_wav import EditWav


class EditWavWindow(tk.Toplevel):
    """
    音频编辑类，包括音频的播放、删除等。窗口为模态窗
    """
    def __init__(self, parent, title: str, file_path_name: str):
        """
        构造函数，进行初始化设置
        :param parent: 父窗口句柄
        :param title: 窗口标题
        :param file_path_name: 音频文件读取目录的路径
        """
        tk.Toplevel.__init__(self, parent, width=620, height=420)
        self.geometry("600x400+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 30))
        self.title(title)
        self.resizable(height=False, width=False)
        self.grab_set()  # 设置模态

        # 属性
        self.__path_wav = file_path_name
        self.__edit_wav = EditWav(self.__play_wav_callback)   # 创建并初始化音频播放类对象
        self.__play_wav_name = ""     # 正在播放的音频文件名
        self.__select_wav_name = self.__play_wav_name   # 选中的音频文件名
        self.__play_index = 0     # 正在播放的音频文件在listbox控件中的索引
        self.__select_index = 0  # 当前选中项索引号
        self.__quit_window = False    # 窗口关闭标记
        self.__begin_flag = False     # 开始播放标记

        # 关闭窗口按钮注册响应事件
        self.protocol('WM_DELETE_WINDOW', self.__close_window)
        # 标签
        self.log_text = tk.StringVar()
        self.log_text.set("当前默认选中首项")
        self.record_file_label = tk.Label(self, text="录音文件")
        self.record_file_label.grid(row=0, column=0, sticky=tk.N)
        self.result_data_label = tk.Label(self, textvariable=self.log_text, font=("微软雅黑", 10), foreground='red',
                                          background='LightYellow', relief=tk.GROOVE)
        self.result_data_label.grid(row=4, column=0, ipadx=2, pady=3, columnspan=2, sticky=tk.S)
        # 鼠标右键菜单
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="播放/暂停", command=self.__begin_pause_play)
        self.menu.add_separator()
        self.menu.add_command(label="停止", command=self.__stop_play)
        self.menu.add_separator()
        self.menu.add_command(label="删除", command=self.__delete_wav)
        # ListBox控件
        self.listbox = tk.Listbox(self, width=32, height=19)
        self.listbox.grid(row=1, column=0, ipadx=10, rowspan=3)
        self.listbox.bind("<Button-1>", self.__single_click)  # 绑定单击事件
        self.listbox.bind("<Double-Button-1>", self.__double_click)
        self.__get_wav_list_to_listbox(self.__path_wav)
        # 绑定右键菜单
        self.listbox.bind("<Button-3>", self.__popupmenu)
        # 为listbox控件绑定滑动条
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=1, column=1, sticky=tk.NSEW, rowspan=3)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        # 进度条
        self.progressbar = ttk.Progressbar(self, length=240, cursor='spider', mode="determinate", orient=tk.HORIZONTAL)
        self.progressbar.grid(row=1, column=2)

        # 工具栏
        self.__set_toolbar()

    def __set_toolbar(self):
        """
        设置工具栏
        """
        toolbar = tk.Frame(self, bd=1, relief=tk.FLAT)
        images = [ImageTk.PhotoImage(Image.open("image/last.png")),
                  ImageTk.PhotoImage(Image.open("image/begin_pause.png")),
                  ImageTk.PhotoImage(Image.open("image/stop.png")),
                  ImageTk.PhotoImage(Image.open("image/next.png"))]
        img_w_h = 33

        last_btn = tk.Button(toolbar, image=images[0], width=img_w_h, height=img_w_h, relief=tk.FLAT,
                             command=self.__last_wav)
        last_btn.image = images[0]
        last_btn.grid(row=0, column=1, padx=3, pady=2)

        begin_pause_btn = tk.Button(toolbar, image=images[1], width=img_w_h, height=img_w_h, relief=tk.FLAT,
                                    command=self.__begin_pause_play)
        begin_pause_btn.image = images[1]
        begin_pause_btn.grid(row=0, column=2, padx=3, pady=2)

        stop_btn = tk.Button(toolbar, image=images[2], width=img_w_h, height=img_w_h, relief=tk.FLAT,
                             command=self.__stop_play)
        stop_btn.image = images[2]
        stop_btn.grid(row=0, column=3, padx=3, pady=2)

        next_btn = tk.Button(toolbar, image=images[3], width=img_w_h, height=img_w_h, relief=tk.FLAT,
                             command=self.__next_wav)
        next_btn.image = images[3]
        next_btn.grid(row=0, column=4, padx=3, pady=2)

        toolbar.grid(row=3, column=2, sticky=tk.NSEW, padx=70, rowspan=2)

    def __popupmenu(self, event):
        """
        弹出菜单,对右键菜单进行弹出
        :param event: 鼠标事件
        """
        self.menu.post(event.x_root, event.y_root)

    def __play_wav_callback(self, choice: str, value: str):
        """
        音频播放类的回调函数，用来返回进度条值和设置__begin_flag
        :param choice: 选项，"progressbar"：更新进度条，"begin_flag"：设置__begin_flag
        :param value: 传回用来设置的值
        """
        if choice == "progressbar":
            self.__update_progressbar(value)
        elif choice == "begin_flag":
            self.__begin_flag = value

    def __update_progressbar(self, var):
        """
        刷新进度条
        :param var: 进度条的值（0~100）
        """
        if not self.__quit_window:
            self.progressbar["value"] = var
            self.update()

    def __begin_pause_play(self):
        """
        播放/暂停事件响应函数，对播放/暂停进行控制，以及播放线程的创建
        """
        if len(self.__select_wav_name) > 0:
            if self.__edit_wav.play_status == self.__edit_wav.RUN:
                self.__edit_wav.play_status = self.__edit_wav.PAUSE
            else:
                self.__edit_wav.play_status = self.__edit_wav.RUN
            if not self.__begin_flag:
                self.__edit_wav.play_status = self.__edit_wav.RUN
                recog_thread = threading.Thread(target=self.__play_wav)  # 创建一个线程
                recog_thread.setDaemon(True)  # 设为保护线程，主进程结束会关闭线程
                recog_thread.start()  # 启动线程
                self.__begin_flag = True
        else:
            self.log_text.set("请先选中要播放的条目！")

    def __play_wav(self):
        """
        播放音频文件
        """
        self.log_text.set("正在播放 " + self.__select_wav_name)
        self.__play_wav_name = self.__path_wav + self.__select_wav_name
        self.__play_index = self.__select_index
        self.__edit_wav.play_wav(self.__play_wav_name)

    def __stop_play(self):
        """
        “结束”按钮的响应函数，结束当前播放的音频，终止播放线程
        """
        if self.__begin_flag:
            self.__edit_wav.play_status = self.__edit_wav.STOP
            self.__begin_flag = False
            self.progressbar["value"] = 0
            self.log_text.set("当前选中 " + self.__select_wav_name)

    def __last_wav(self):
        """
        “上一个”按钮的响应函数，选中上一个项目
        """
        if self.__select_index > 0:
            self.__select_index = self.__select_index - 1
        else:
            self.__select_index = self.listbox.size() - 1
        self.__select_item()

    def __next_wav(self):
        """
        “下一个”按钮的响应函数，选中下一个项目
        """
        if self.__select_index < (self.listbox.size() - 1):
            self.__select_index = self.__select_index + 1
        else:
            self.__select_index = 0
        self.__select_item()

    def __select_item(self):
        """
        对选中项进行处理，获取选中项的名字、设置选中项等
        """
        select_text = self.listbox.get(self.__select_index)  # 得到选中项
        self.__select_wav_name = select_text.split(']')[-1]  # 截取选中项中的文件名
        self.listbox.selection_clear(0, 'end')  # 取消所有选中项
        self.listbox.selection_set(self.__select_index)  # 设置为选中项
        self.log_text.set("当前选中 " + self.__select_wav_name)

    def __get_wav_list_to_listbox(self, file_path):
        """
        获取录音文件存储目录中的所有音频文件，并将其插入listbox控件中
        :param file_path: 音频文件存放的目录
        """
        wav_list = []
        if os.path.exists(file_path):
            for wav_file in os.listdir(file_path):
                if wav_file.endswith('.wav'):
                    wav_list.append(wav_file)
        count = 0
        for wav_file in wav_list:
            count += 1
            wav_file = "[" + str(count) + "]" + wav_file
            self.listbox.insert(tk.END, wav_file)

    def __single_click(self, event):
        """
        单击鼠标选中listbox控件中的条目
        """
        self.__select_index = event.widget.nearest(event.y)  # 得到选中项的索引号
        select_text = self.listbox.get(self.__select_index)  # 得到选中项内容
        self.__select_wav_name = select_text.split(']')[-1]  # 截取选中项中的文件名

    def __double_click(self, event):
        """
        双击鼠标播放（暂停）选中的音频文件
        """
        if self.__play_wav_name != self.__path_wav + self.__select_wav_name:
            self.__stop_play()    # 结束当前播放线程
            time.sleep(0.3)     # 延时，保证当前播放线程已结束
            self.__play_wav_name = self.__select_wav_name
        self.__begin_pause_play()

    def __delete_wav(self):
        """
        删除listbox控件中选中的条目
        """
        if len(self.__select_wav_name) and os.path.exists(self.__path_wav + self.__select_wav_name):
            msg = "确认要删除" + self.__select_wav_name + "吗？"
            flag = tk.messagebox.askokcancel('提示', msg)  # 确定/取消，返回值true/false
            if flag:
                os.remove(self.__path_wav + self.__select_wav_name)
                self.listbox.delete(self.__select_index)
                tk.messagebox.showinfo("提示", "删除成功！")
        else:
            tk.messagebox.showwarning("警告", "请选中条目后再进行删除操作！")

    def __close_window(self):
        """
        关闭模态窗口，需要结束未结束的播放线程
        """
        self.__quit_window = True
        self.__edit_wav.play_status = self.__edit_wav.STOP
        self.destroy()


if __name__ == "__main__":
    file_path_names = os.getcwd().replace('\\', '/') + "/"  # "D:/course_data/pycharm_workspace/esp/"
    file_name_wav = file_path_names + "record/" + "wav/"
    init_window = tk.Tk()  # 实例化出一个父窗口
    sub_window = EditWavWindow(init_window, "音频记录编辑窗口", file_name_wav)
    # label控件显示图片
    sub_window.mainloop()
