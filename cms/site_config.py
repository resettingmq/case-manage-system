# -*- coding: utf-8 -*-


# 配置infobox的信息
INFO_BOXES = {
    'client': {
        'model': 'base:client'
    }
}


# 用于配置各View的信息
# 需要在View中指定view_name属性，来获取这个dict中相应的值
VIEWS = {
    'index': {
        'INFO_BOXES': ['client']
    }
}