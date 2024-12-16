'''
Список обязательных параметров: Например, IP-адрес оборудования, тип теста и т.д.
Список необязательных параметров: Например, таймаут, количество повторений и т.д.
Функции для валидации параметров: Проверка корректности введенных параметров.
'''
import argparse

def parse_params(args):
    config_params = {}
    if args.param:
        for param in args.param:
            key, value = param.split('=')
            config_params[key] = value
    return config_params
