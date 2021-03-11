#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-10 15:35:45
Description: None
Version: 1.0
License: None
"""


from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'id': user.id,
        'username': user.username
    }


class PageNum(PageNumberPagination):
    """自定义分页器"""

    page_size_query_param = 'pagesize'
    max_page_size = 10

    # 重写PageNumberPagination中的get_paginated_response方法以达成想要的格式
    def get_paginated_response(self, data):

        # return Response(OrderedDict([
        #     ('count', self.page.paginator.count),
        #     ('next', self.get_next_link()),
        #     ('previous', self.get_previous_link()),
        #     ('results', data)
        # ]))

        return Response(
            {
                'count':self.page.paginator.count,
                'lists':data,
                'page':self.page.number,
                'pages':self.page.paginator.num_pages,
                'pagesize': self.max_page_size
            }
        )
