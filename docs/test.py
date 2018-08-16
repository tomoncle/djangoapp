#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time           : 18-8-15 下午6:33
# @Author         : Tom.Lee
# @File           : test.py
# @Product        : PyCharm
# @Docs           : 
# @Source         : 

# # 以二进制模式打开文件
# write_file = open('a.f', 'wb')
#
# # 以二进制模式读取文件　
# with open('/tmp/dl.f', 'rb') as f:
#     for line in f:
#         # line 为bytes数组
#         write_file.write(line)
#
# write_file.close()
# # diff a.f /tmp/dl.f 相同
import re

print(re.match(r'\d*', '--'))