"""wxcloudrun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from wxcloudrun import drawviews
from django.conf.urls import url

urlpatterns = (

    # 查询中签结果
    url(r'^^api/draw/query(/)?$', drawviews.query),

    # 查询转债信息
    url(r'^^api/query/bond(/)?$', drawviews.query_bond),

    # 生成文章
    url(r'^^api/gen/doc(/)?$', drawviews.gen_doc),

    # 生成文章页
    url(r'^^doc(/)?$', drawviews.doc_index),

    # 微信认证
    url(r'^^wx(/)?$', drawviews.wechat_validate),

    # 获取主页
    url(r'(/)?$', drawviews.index),
)
