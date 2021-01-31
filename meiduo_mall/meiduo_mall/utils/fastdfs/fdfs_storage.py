from django.core.files.storage import Storage
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义文件存储类"""

    #
    # def __init__(self, option=None):
    #     """文件存储类的初始化方法"""
    #     if not option:
    #         option = settings.CUSTOM_STORAGE_OPTIONS
    #
    #     pass

    def _open(self, name, mode='rb'):
        """
        打开文件时会被调用的方法：必须重写
        :param name: 文件路径
        :param mode: 文件打开方式
        :return: None
        """

        pass

    def _save(self, name, content):
        """
        保存文件时会被调用的方法：必须重写
        :param name: 文件路径
        :param content: 文件二级制内容
        :return: None
        """

        pass

    def url(self, name):
        """
        返回name所指文件的绝对路径
        :param name: 文件的相对路径
        :return: 文件的全路径：http://IP:8888/相对路径
        """

        return 'http://127.0.0.1:8888/' + name
