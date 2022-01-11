#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : espnet_recognize.py
# @Software   : PyCharm
# @Description：espnet识别类

import soundfile
from asr_inference import Speech2Text


class EspnetRecognize:
    """
    espnet相关设置和识别
    """
    def __init__(self):
        self.__path_asr_config = "exp/asr_train_asr_conformer3_raw_char_batch_bins4000000_accum_grad4_sp/config.yaml"
        self.__path_asr_file = "exp/asr_train_asr_conformer3_raw_char_batch_bins4000000_accum_grad4_sp/valid.acc.ave_10best.pth"
        # self.__path_lm_config = "exp/lm_train_lm_transformer_char_batch_bins2000000/config.yaml"
        # self.__path_lm_file = "exp/lm_train_lm_transformer_char_batch_bins2000000/valid.loss.ave_10best.pth"

        self.__speech2text = Speech2Text(asr_train_config=self.__path_asr_config, asr_model_file=self.__path_asr_file)
        # lm_train_config=self.__path_lm_config, lm_file=self.__path_lm_file
        self.select_mandarin = True

    def set_mandarin_flag(self, select_mandarin):
        self.select_mandarin = select_mandarin

    def select_asr_model(self):
        self.__path_asr_config = "exp/asr_train_asr_conformer3_raw_char_batch_bins4000000_accum_grad4_sp/config.yaml"
        self.__path_asr_file = "exp/asr_train_asr_conformer3_raw_char_batch_bins4000000_accum_grad4_sp/valid.acc.ave_10best.pth"
        if not self.select_mandarin:
            self.__path_asr_config = "exp/asr_train_asr_conformer_raw_zh_char_sp/config.yaml"
            self.__path_asr_file = "exp/asr_train_asr_conformer_raw_zh_char_sp/valid.acc.ave_10best.pth"

        self.__speech2text = Speech2Text(asr_train_config=self.__path_asr_config, asr_model_file=self.__path_asr_file)

    def speech_to_text(self, path_wav_to_recog):
        """
        音频文件识别函数，识别的入口
        :param path_wav_to_recog: 需要进行识别的音频文件的绝对路径
        :return result_recog: 返回识别结果字符串
        """
        self.select_asr_model()
        audio, rate = soundfile.read(path_wav_to_recog)
        result_recog_all = self.__speech2text(audio)
        result_recog_tuple = result_recog_all[0]
        result_recog = result_recog_tuple[0]
        return result_recog
