#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : gui.py
# @Software   : PyCharm
# @Description：gui窗口类

import os
import wave
import tkinter as tk
from tkinter import messagebox
import time
import datetime
import threading
from PIL import Image, ImageTk
import shutil

from record_wav import RecordWav
from edit_wav import EditWav
from record_text import RecordText
from edit_wav_window import EditWavWindow
from file_dialog import FileDialog
from interview_set import InterviewSet
from recognize_thread import RecognizeThread
from volume_set import VolumeSet


class MyGui:
    """
    交互界面类，进行相应操作的一些控制等
    """

    def __init__(self, init_window_name, window_title):
        """
        构造函数，进行相应的窗口初始化、录音线程的启动、识别类对象的创建等
        :param init_window_name: 主窗口句柄
        :param window_title: 主窗口标题
        """
        self.init_window_name = init_window_name
        self.window_title = window_title
        # 设置窗口
        # 窗口
        self.init_window_name.title(window_title)  # 窗口名
        self.init_window_name.geometry('800x600+220+20')  # 800x560为窗口大小，+220+50定义窗口弹出时的默认展示位置
        # self.init_window_name["bg"] = "SkyBlue"          #窗口背景色，其他背景色见：blog.csdn.net/chl0000/article/details/7657887
        # self.init_window_name.attributes("-alpha",0.9)      #虚化，值越小虚化程度越高
        self.init_window_name.resizable(height=False, width=False)
        # 菜单
        self.init_menu = tk.Menu(self.init_window_name)  # 创建根菜单
        self.menu4_1 = tk.Menu()
        self.menu4_2 = tk.Menu()
        self.__set_menu()
        # 工具栏
        self.__set_toolbar()
        # 识别结果框、日志框、状态框。标签、文本框、滑动条
        # 识别结果、日志与状态面板的父面板
        text_frame = tk.Frame(self.init_window_name, width=120, height=10, relief=tk.RIDGE)
        # 识别结果面板
        result_frame = tk.Frame(text_frame, width=110, relief=tk.RIDGE)
        self.result_data_label = tk.Label(result_frame, text="识别结果")
        self.result_data_label.grid(row=0, column=0)
        self.__result_data_text = tk.Text(result_frame, width=107, height=30)  # 识别结果文本框
        self.__result_data_text.grid(row=12, column=0, padx=0, columnspan=1)
        scrollbar0 = tk.Scrollbar(result_frame)
        scrollbar0.grid(row=12, column=2, columnspan=1, sticky=tk.NSEW)
        scrollbar0.config(command=self.__result_data_text.yview)
        self.__result_data_text.config(yscrollcommand=scrollbar0.set)
        result_frame.grid(row=0, column=0, padx=15, columnspan=20)

        # 日志和状态面板的父面板
        log_status_frame = tk.Frame(text_frame, relief=tk.RIDGE)
        # 日志面板
        log_frame = tk.Frame(log_status_frame, relief=tk.RIDGE)
        self.log_label = tk.Label(log_frame, text="日志")
        self.log_label.grid(row=0, column=0)
        self.__log_data_text = tk.Text(log_frame, width=52, height=8)  # 日志文本框
        self.__log_data_text.grid(row=12, column=0, padx=0, columnspan=10)
        scrollbar1 = tk.Scrollbar(log_frame)
        scrollbar1.grid(row=12, column=11, columnspan=1, sticky=tk.NSEW)
        scrollbar1.config(command=self.__log_data_text.yview)
        self.__log_data_text.config(yscrollcommand=scrollbar1.set)
        log_frame.grid(row=160, column=0, padx=0, columnspan=11, sticky=tk.W)
        # 状态面板
        status_frame = tk.Frame(log_status_frame, relief=tk.RIDGE)
        self.status_label = tk.Label(status_frame, text="状态")
        self.status_label.grid(row=0, column=0)
        self.__status_data_text = tk.Text(status_frame, width=52, height=8)  # 状态文本框
        self.__status_data_text.grid(row=12, column=0, padx=0, columnspan=10)
        scrollbar2 = tk.Scrollbar(status_frame)
        scrollbar2.grid(row=12, column=11, columnspan=1, sticky=tk.NSEW)
        scrollbar2.config(command=self.__status_data_text.yview)
        self.__status_data_text.config(yscrollcommand=scrollbar2.set)
        status_frame.grid(row=160, column=12, padx=0, columnspan=11, sticky=tk.W)
        log_status_frame.grid(row=1, column=0, padx=15, sticky=tk.W, columnspan=22)

        # 版本
        app_version = tk.Frame(text_frame, width=107, bd=1, relief=tk.RIDGE)
        version_label = tk.Label(app_version, text="版本1.0")
        version_label.grid(row=0, column=0, sticky=tk.W, ipadx=10)
        blank_label = tk.Label(app_version, text="")  # 占位
        blank_label.grid(row=0, column=1, sticky=tk.W, ipadx=300)
        current_date = "日期：" + str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
        date_label = tk.Label(app_version, text=current_date)
        date_label.grid(row=0, column=2, sticky=tk.NSEW)
        app_version.grid(row=2, column=0, sticky=tk.NSEW, pady=5, columnspan=22)

        text_frame.grid(row=12, column=0, sticky=tk.W, columnspan=22)

        # 属性
        self.__record_text = RecordText(self.write_log_status)  # 文本记录对象
        self.__record_wav = RecordWav(self.write_log_status)  # 录音类对象
        self.__edit_wav = EditWav(self.write_log_status)  # 播放器对象

        self.__select_mandarin = True  # True识别普通话，False识别西咸方言
        self.__single_recognize = True  # True单次识别，False连续识别
        self.__log_count = 0  # 对打印的日志条数进行计数
        self.__status_count = 0  # 对打印的状态条数进行计数
        self.__interviewer_name = ""  # 被约谈人
        self.__file_path_name = os.getcwd().replace('\\', '/') + "/"  # "D:/course_data/pycharm_workspace/esp/"
        self.__file_name_wav = self.__file_path_name + "record/" + self.__interviewer_name + "wav/"
        self.__file_name_doc = self.__file_path_name + "record/" + self.__interviewer_name + "doc/record"

        self.__event = threading.Event()
        self.__record_thread = threading.Thread(target=self.__speech_recognize)  # 创建录音线程
        self.__record_thread.setDaemon(True)  # 设为保护线程，主进程结束会关闭线程
        self.__record_thread.start()  # 启动线程

        self.__recognize_thread = RecognizeThread(self.recog_callback)  # 创建识别线程类对象

        self.write_status_text("系统准备就绪")

    def __set_menu(self):
        """
        菜单栏设置
        """
        self.init_window_name['menu'] = self.init_menu  # 顶级菜单关联根窗体
        menu1 = tk.Menu(self.init_menu, tearoff=False)  # 创建子菜单(父级,去横线)
        menu2 = tk.Menu(self.init_menu, tearoff=False)
        menu3 = tk.Menu(self.init_menu, tearoff=False)
        menu4 = tk.Menu(self.init_menu, tearoff=False)
        menu5 = tk.Menu(self.init_menu, tearoff=False)
        menu6 = tk.Menu(self.init_menu, tearoff=False)

        self.menu4_1 = tk.Menu(menu4, tearoff=False)
        self.menu4_2 = tk.Menu(menu4, tearoff=False)
        menu5_1 = tk.Menu(menu5, tearoff=False)
        menu5_2 = tk.Menu(menu5, tearoff=False)

        self.init_menu.add_cascade(label='文件', menu=menu1)  # 创建顶级菜单栏，并关联子菜单
        self.init_menu.add_cascade(label='编辑', menu=menu2)
        self.init_menu.add_cascade(label='约谈设置', menu=menu3)
        self.init_menu.add_cascade(label='识别设置', menu=menu4)
        self.init_menu.add_cascade(label='约谈记录', menu=menu5)
        self.init_menu.add_cascade(label='帮助', menu=menu6)

        menu1.add_command(label='识别音频文件', command=self.__open_wav_recognize)  # 子菜单栏
        menu1.add_separator()  # 分割线
        menu1.add_command(label='退出', command=self.__quit_gui)
        menu2.add_command(label='清空结果', command=self.__clear_result)
        menu2.add_command(label='清空日志', command=self.__clear_log)
        menu2.add_command(label='清空状态', command=self.__clear_status)
        menu2.add_separator()  # 分割线
        menu2.add_command(label='全部清空', command=self.__clear_all_ctrl)
        menu3.add_command(label='被约谈人', command=self.__set_interviewer)
        menu4.add_cascade(label='语言', menu=self.menu4_1)
        menu4.add_separator()  # 分割线
        menu4.add_cascade(label='识别方式', menu=self.menu4_2)
        menu4.add_separator()  # 分割线
        menu4.add_command(label='识别音量设置', command=self.__set_volume)
        menu5.add_cascade(label='音频记录', menu=menu5_1)
        menu5.add_separator()  # 分割线
        menu5.add_cascade(label='文本记录', menu=menu5_2)
        menu6.add_command(label='关于', command=self.__about_msg)

        # menu4_1、menu4_2由于要进行默认选中，所以只能进行回溯，其实现放在set_init_menu(self, user_choice)中
        menu5_1.add_command(label='编辑录音', command=self.__edit_record_wav)
        menu5_1.add_command(label='合并录音', command=self.__merge_wav)
        menu5_2.add_command(label='打开', command=self.__open_record_doc)
        menu5_2.add_command(label='关闭', command=self.__close_record_doc)
        menu5_2.add_separator()  # 分割线
        menu5_2.add_command(label='追加保存', command=self.__save_record1_doc)
        menu5_2.add_command(label='覆盖保存', command=self.__save_record2_doc)
        menu5_2.add_separator()  # 分割线
        menu5_2.add_command(label='删除', command=self.__delete_record_doc)

    def set_init_menu(self, *user_choice):
        """
        对需要进行回溯的菜单项进行设置，以便实现默认选中出现勾选状态
        :param user_choice: 选中项（0、1...）
        """
        self.menu4_1.add_radiobutton(label='普通话', variable=user_choice[0], value=0, command=self.__mandarin)
        self.menu4_1.add_radiobutton(label='陕西方言', variable=user_choice[0], value=1, command=self.__xi_xian_mandarin)
        self.menu4_2.add_radiobutton(label='单次识别', variable=user_choice[1], value=0, command=self.__single_time)
        self.menu4_2.add_radiobutton(label='连续识别', variable=user_choice[1], value=1, command=self.__consecutive)
        user_choice[0].set(0)  # 初始选中第一项
        user_choice[1].set(0)  # 初始选中第一项

    def __set_toolbar(self):
        """
        工具栏设置
        """
        toolbar = tk.Frame(self.init_window_name, bd=1, width=120, relief=tk.RIDGE)
        images = [ImageTk.PhotoImage(Image.open("image/begin.png")),
                  ImageTk.PhotoImage(Image.open("image/stop.png"))]

        begin_btn = tk.Button(toolbar, image=images[0], width=10, height=10, relief=tk.FLAT,
                              command=self.__begin_recognize)
        begin_btn.image = images[0]
        begin_btn.grid(row=0, column=0, padx=3, pady=2)
        pause_btn = tk.Button(toolbar, image=images[1], width=10, height=10, relief=tk.FLAT,
                              command=self.__quit_recognize)
        pause_btn.image = images[1]
        pause_btn.grid(row=0, column=1, padx=3, pady=2)

        toolbar.grid(row=0, column=0, sticky=tk.NSEW, columnspan=22)

    # 功能函数
    def __update_path_name(self):
        """
        更新路径，设置识别人信息后对识别记录文件存储路径进行修改
        """
        today_date = str(datetime.date.today()).replace('-', '')
        name = self.__interviewer_name
        self.__file_name_wav = self.__file_path_name + "record/" + name + "/" + "wav/"
        self.__file_name_doc = self.__file_path_name + "record/" + name + "/" + "doc/" + name + today_date

    def __quit_gui(self):
        """
        退出系统
        """
        self.init_window_name.destroy()

    def __open_wav_recognize(self):
        """
        识别外部音频文件，打开外部音频文件并识别，识别结果在识别结果框显示
        """
        file_dialog = FileDialog(self.init_window_name, "识别外部音频文件", ".wav")
        open_file_path = file_dialog.get_open_file_name()
        if len(open_file_path) > 0:
            msg = "您选定的音频文件的路径为：" + open_file_path + "，您是否要识别此音频文件"
            flag = tk.messagebox.askyesno('提示', msg)  # 是/否，返回值true/false
            if flag:
                if not open_file_path.endswith('.wav'):  # 判断是否为wav格式，如果不是，将其格式转换为wav再识别
                    # 音频文件格式转换为wav、单通道等，转换成功返回绝对路径，失败返回空字符串
                    open_file_path = self.__edit_wav.format_to_wav(open_file_path)
                if len(open_file_path) > 0:
                    self.__recognize_thread.recognize(open_file_path)
                else:
                    tk.messagebox.showerror('错误', "识别失败，您选择的音频文件无法识别！")
        else:
            tk.messagebox.showerror('错误', "文件路径获取失败！")

    def __clear_all_ctrl(self):
        """
        清空所有text控件内容
        """
        self.__clear_result()
        self.__clear_log()
        self.__clear_status()

    def __clear_result(self):
        """
        清空识别结果框
        """
        self.__result_data_text.delete('1.0', 'end')

    def __clear_log(self):
        """
        清空日志栏
        """
        self.__log_count = 0
        self.__log_data_text.delete('1.0', 'end')

    def __clear_status(self):
        """
        清空状态栏
        """
        self.__status_count = 0
        self.__status_data_text.delete('1.0', 'end')

    def interviewer_callback(self, interview_name: str):
        """
        设置识别人信息窗口类的回调函数，用来回调设置识别人信息
        :param interview_name: 识别人姓名的拼音
        """
        self.__interviewer_name = interview_name
        self.__update_path_name()

    def __set_interviewer(self):
        """
        约谈人信息设置
        """
        interview = InterviewSet(self.interviewer_callback, self.init_window_name, "约谈人设置窗口",
                                 self.__file_path_name + "record/")
        interview.mainloop()

    def __mandarin(self):
        """
        普通话识别
        """
        self.__select_mandarin = True
        self.__recognize_thread.espnet_recog.set_mandarin_flag(self.__select_mandarin)

    def __xi_xian_mandarin(self):
        """
        陕西方言识别
        """
        self.__select_mandarin = False
        self.__recognize_thread.espnet_recog.set_mandarin_flag(self.__select_mandarin)

    def __single_time(self):
        """
        单次识别
        """
        self.__single_recognize = True

    def __consecutive(self):
        """
        连续识别
        """
        self.__single_recognize = False

    def __set_volume(self):
        """
        设置识别声音幅值大小，设置值以下的幅值均被认为是噪音
        """
        volume_set = VolumeSet(self.__record_wav, self.init_window_name, "识别音量设置窗口")
        volume_set.mainloop()

    def __speech_recognize(self):
        """
        进行语音识别的入口，录音线程的注册函数
        """
        while True:
            self.__event.wait()
            if self.__record_wav.status == self.__record_wav.RUN:
                new_wav_path_name = self.__creat_wav_path_name()  # 生成wav文件名
                if self.__record_wav.record(new_wav_path_name):  # 录音
                    self.write_status_text("正在进行识别")
                    self.__recognize_thread.recognize(new_wav_path_name)  # 识别
            if not self.__single_recognize:
                self.__record_wav.status = self.__record_wav.RUN
            else:
                self.__event.clear()
                self.write_status_text("识别结束")
                self.write_status_text("系统准备就绪")

    def __creat_wav_path_name(self):
        """
        创建新的wav文件路径，用来保存录音
        :return: 返回创建的文件路径
        """
        microsecond = str(datetime.datetime.now().microsecond).zfill(6)
        current_time = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + microsecond
        path_name = self.__file_name_wav + current_time + ".wav"
        return path_name

    def recog_callback(self, result):
        """
        识别线程回调函数，传回识别结果
        :param result: 识别结果
        """
        if len(result) != 0:
            result = result + "\n"
            self.__result_data_text.insert(tk.END, result)
            self.write_log_text("INFO:识别成功")
        else:
            self.write_log_text("INFO:识别结果为空")
        self.write_status_text("识别完成，录音准备就绪")

    def __begin_recognize(self):
        """
        “开始识别”按钮的响应函数，开始识别，创建并启动录音识别线程
        """
        self.__event.set()
        self.__record_wav.status = self.__record_wav.RUN

    def __quit_recognize(self):
        """
        ”识别终止“按钮的响应函数，终止识别
        """
        self.__event.clear()
        self.__record_wav.status = self.__record_wav.STOP

    def __open_record_doc(self):
        """
        打开记录文本文件
        """
        file_path_name = self.__file_name_doc + "." + self.__record_text.file_type
        if not os.path.exists(file_path_name):
            self.__record_text.save_record_doc(self.__file_name_doc, "w", "")
        self.__record_text.open_record_doc(self.__file_name_doc)

    def __close_record_doc(self):
        """
        关闭文件
        """
        self.__record_text.close_record_doc(self.__file_name_doc)

    def __save_record1_doc(self):
        """
        追加保存
        """
        record_text = str(self.__result_data_text.get('0.0', 'end'))
        self.__record_text.save_record_doc(self.__file_name_doc, "a", record_text)
        self.__save_record_doc(self.__file_name_doc)

    def __save_record2_doc(self):
        """
        覆盖保存
        """
        record_text = str(self.__result_data_text.get('0.0', 'end'))
        self.__record_text.save_record_doc(self.__file_name_doc, "w", record_text)
        self.__save_record_doc(self.__file_name_doc)

    def __save_record_doc(self, file_path_name):
        """
        文本记录文件保存操作的提示信息
        :param file_path_name: 文件的绝对路径
        """
        file_path_name = file_path_name + "." + self.__record_text.file_type
        if os.path.exists(file_path_name):
            msg = "保存成功，保存路径为：" + self.__file_name_doc + " ！"
            tk.messagebox.showinfo('提示', msg)
        else:
            tk.messagebox.showinfo('提示', "操作失败！")

    def __delete_record_doc(self):
        """
        删除记录文本文件
        """
        self.__record_text.delete_record_doc(self.__file_name_doc)
        if not os.path.exists(self.__file_name_doc):
            tk.messagebox.showinfo('提示', "删除成功！")
        else:
            tk.messagebox.showinfo('提示', "删除失败！")

    def __edit_record_wav(self):
        """
        编辑录音文件子窗口调用入口
        """
        sub_window = EditWavWindow(self.init_window_name, "音频记录编辑窗口", self.__file_name_wav)
        # label控件显示图片
        image = ImageTk.PhotoImage(file='image/player.png')
        label_img = tk.Label(sub_window, image=image, width=240, height=240)
        label_img.grid(row=2, column=2, padx=40)
        sub_window.mainloop()

    def __merge_wav(self):
        """
        合并音频记录文件
        """
        merge_path = self.__file_path_name + "record/" + self.__interviewer_name + "/" + "merge.wav"
        self.__edit_wav.merge_wav(self.__file_name_wav, merge_path, self.init_window_name)

    def write_log_status(self, choice: str, msg: str):
        if choice == "log":
            self.write_log_text(msg)
        elif choice == "status":
            self.write_status_text(msg)

    def write_log_text(self, logmsg):
        """
        日志动态打印
        :param logmsg: 日志内容
        """
        self.__log_count += 1
        current_time = get_current_time()
        logmsg_in = "[" + str(self.__log_count) + "]" + str(current_time) + " " + str(logmsg) + "\n"  # 换行
        self.__log_data_text.insert(tk.END, logmsg_in)

    def write_status_text(self, status_msg):
        """
        运行状态动态打印
        :param status_msg: 状态内容
        """
        self.__status_count += 1
        current_time = get_current_time()
        status_text = "[" + str(self.__status_count) + "]" + str(current_time) + " " + str(status_msg) + "\n"
        self.__status_data_text.insert(tk.END, status_text)

    def __about_msg(self):
        """
        有关此应用程序的一些信息
        """
        app_name = "应用名称：" + self.window_title + "\n"
        app_version = "项目版本：1.0"

        msg = app_name + app_version
        tk.messagebox.showinfo('about', msg)


def get_current_time():
    """
    获取当前时间
    :return: 返回获取的年月日时分秒
    """
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return current_time


def gui_start():
    """
    gui启动入口
    """
    init_window = tk.Tk()  # 实例化出一个父窗口
    gui = MyGui(init_window, "交通行政执法笔录生成系统")
    user_choice = [tk.IntVar(), tk.IntVar()]
    gui.set_init_menu(*user_choice)
    print(gui.init_window_name.title() + "gui is running")
    init_window.mainloop()  # 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示


if __name__ == "__main__":
    gui_start()
