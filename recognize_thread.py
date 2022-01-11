#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : recognize_thread.py
# @Software   : PyCharm
# @Description：识别线程类

import queue
import threading
import os
from espnet_recognize import EspnetRecognize


class RecognizeThread:
    """
    识别线程类
    """

    def __init__(self, callback):
        """
        构造函数，完成初始化，以及创建识别线程
        :param callback: 回调函数，用来回传识别结果，参数：result
        """
        self.__mutex = threading.Lock()  # 初始化互斥量
        self.__cond = threading.Condition(self.__mutex)  # 初始化条件变量
        self.__recog_queue = queue.Queue()  # 初始化识别队列

        self.espnet_recog = EspnetRecognize()  # 创建espnet识别类对象
        self.__callback = callback  # 回调函数
        self.__recog_thread = threading.Thread(target=self.__process)  # 创建一个线程
        self.__recog_thread.setDaemon(True)  # 设为保护线程，主进程结束会关闭线程
        self.__recog_thread.start()  # 启动线程

    def __get(self):
        """
        获取识别队列的队首元素
        :return elem: 取到的元素
        """
        # 获取互斥锁和条件变量，python中threading条件变量默认包含互斥量，因此只需要获取条件变量即可
        if self.__cond.acquire():  # 加锁
            while self.__recog_queue.empty():
                self.__cond.wait()  # 条件变量等待，阻塞
            elem = self.__recog_queue.get()  # 取队首元素
            self.__cond.release()  # 释放

            return elem

    def recognize(self, elem):
        """
        将待识别的文件绝对路径加入识别队列，唤醒识别线程
        :param elem: 录音文件的路径
        """
        if self.__cond.acquire():
            self.__recog_queue.put(elem)
            self.__cond.notify()  # 唤醒阻塞线程
            self.__cond.release()

    def __process(self):
        """
        识别线程，对识别队列中的音频文件进行识别，并调用回调函数将识别结果传回
        """
        while True:
            wav_file_name = self.__get()
            result = self.espnet_recog.speech_to_text(wav_file_name)  # 识别
            self.__callback(result)  # 调用回调函数
            if len(result) == 0 and os.path.exists(wav_file_name):
                os.remove(wav_file_name)  # 删除识别为空的音频记录


if __name__ == "__main__":
    queue = RecognizeThread(lambda x: print(x))
    run = True


    def th1():
        for i in range(10):
            queue.recognize(i)


    def th2():
        while run:
            print(queue.__get())
            print(queue.__get())


    recog_thread1 = threading.Thread(target=th1)  # 创建一个线程
    recog_thread1.setDaemon(True)  # 设为保护线程，主进程结束会关闭线程
    recog_thread1.start()  # 启动线程

    recog_thread2 = threading.Thread(target=th2)  # 创建一个线程
    recog_thread2.setDaemon(True)  # 设为保护线程，主进程结束会关闭线程
    recog_thread2.start()  # 启动线程

    if input() == "q":
        run = False
