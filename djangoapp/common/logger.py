#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time           : 18-9-20 下午3:33
# @Author         : Tom.Lee
# @File           : logger.py
# @Product        : PyCharm
# @Docs           : 
# @Source         : 

import logging
import logging.handlers
import re

FORMAT_STR = '%(asctime)s %(levelname)s {model} :: %(message)s'


class ConsoleLogger(logging.Logger):
    """
    自定义logger
    examples:
        logger = ConsoleLogger('mode_name')
        logger.info("ok!")
    """

    def __init__(self, name='%(module)s', level=logging.DEBUG):
        super(ConsoleLogger, self).__init__(name, level)
        self.logger_format = '%(asctime)s %(levelname)s {model} :: %(message)s'.format(model=name)
        self.formatter = logging.Formatter(self.logger_format)
        self.handler = logging.StreamHandler()
        self.handler.setFormatter(self.formatter)
        # 给logger添加上handler
        self.addHandler(self.handler)


class FileLogger(logging.Logger):
    """
    自定义logger
    examples:
        logger = FileLogger('file_path','mode_name')
        logger.info("ok!")
    """

    def __init__(self, name='%(module)s', level=logging.DEBUG):
        super(FileLogger, self).__init__(name, level)
        self.log_file_path = '/tmp/logger.log'
        self.logger_format = '%(asctime)s %(levelname)s {model} :: %(message)s'.format(model=name)
        self.formatter = logging.Formatter(self.logger_format)
        # self.file_handler = logging.FileHandler(self.log_file_path)
        self.file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_file_path, when='D', backupCount=7)
        self.file_handler.suffix = '{}.bak'.format(self.file_handler.suffix)
        self.file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.bak$")
        self.file_handler.setFormatter(self.formatter)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(self.formatter)
        self.addHandler(self.file_handler)
        self.addHandler(self.console_handler)
