# dev settings

"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
# print(sys.path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r_h26^$mke!m4fsa&te!(c*czo$#!d0^zf9=l@hj^eb4xv8d+b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'www.meiduo.site',
    '127.0.0.1',
    '172.16.109.2',
]  # type: list


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 全文检索
    'haystack',
    # 定时任务
    'django_crontab',
    # 跨域问题解决
    'corsheaders',

    # 'meiduo_mall.apps.users'  # app [users]
    'users',
    # index advertisement
    'contents',
    # verifications
    'verifications',
    # OAuth
    'oauth',
    # areas: 省市区三级联动
    'areas',
    # goods: 商品数据
    'goods',
    # carts: 购物车
    'carts',
    # orders: 订单结算
    'orders',
    # payment: 对接支付宝
    'payment',
    # meiduo background admin
    'meiduo_admin.apps.MeiduoAdminConfig'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [

    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',  # configure jinja2 template
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'environment': 'meiduo_mall.utils.jinja2_env.jinja2_environment',
        },
    },

    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {  # 写（主机）
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),

        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'Wyl5161696!',
        'NAME': 'meiduo',
    },
    # 'slave': {  # 读（从机）
    #     'ENGINE': 'django.db.backends.mysql',
    #     'HOST': '172.16.109.2',
    #     'PORT': 3307,
    #     'USER': 'root',
    #     'PASSWORD': 'Wyl5161696!',
    #     'NAME': 'meiduo'
    # }
}
# DATABASE_ROUTERS = ['meiduo_mall.utils.db_router.MasterSlaveDBRouter']

# config redis cache
CACHES = {
    "default": {  # default db 0
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {  # session store in db 1
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_code": {  # verify code store in db 2
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    # "verify_code": { # verify_code store to db 3
    #     "BACKEND": "django_redis.cache.RedisCache",
    #     "LOCATION": "redis://172.16.109.2:6379/3",
    #     "OPTIONS": {
    #         "CLIENT_CLASS": "django_redis.client.DefaultClient",
    #     }
    # },
    "history": {  # 用户浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "carts": {  # 购物车
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
# config session db to redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# static url
STATIC_URL = '/static/'
# static dir path
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # whether disable existed loggers
    'formatters': {  # logs display formats
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # filter logs
        'require_debug_true': {  # export log only when 'DEBUG = True'
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # logs handle methods
        'console': {  # export to terminal
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # export to external files
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            # logs file path
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo0.log'),
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # loggers
        'django': {  # loggers named django
            # export log to both terminal and external files
            'handlers': ['console', 'file'],
            'propagate': True,  # whether successively propagate logs
            'level': 'INFO',  # lowest level of logs
        },
    }
}

# 指定自定义用户模型类。语法 --> '子应用.用户模型类'
AUTH_USER_MODEL = 'users.User'

# 指定自定义用户认证后端
# AUTHENTICATION_BACKENDS = ['users.utils.UsernameMobileBackend']
AUTHENTICATION_BACKENDS = ['meiduo_mall.utils.authenticate.MeiduoModelBackend']

# 判断用户是否登录后，指定未登录用户重定向地址
LOGIN_URL = '/login/'

# QQ Login settings params
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

# 配置邮件服务器
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 指定邮件后端
EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
EMAIL_PORT = 25  # 发邮件端口
EMAIL_HOST_USER = 'hmmeiduo@163.com'  # 授权的邮箱
EMAIL_HOST_PASSWORD = 'hmmeiduo123'  # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '美多商城<hmmeiduo@163.com>'  # 发件人抬头
# 邮箱验证链接
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'

# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.fdfs_storage.FastDFSStorage'
# FastDFS相关参数
FDFS_BASE_URL = 'http://172.16.109.2:8888/'
# FDFS_BASE_URL = 'http://image.meiduo.site:8888/'

# Haystack - elasticsearch api
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://172.16.109.2:9200/',  # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo_mall',  # Elasticsearch建立的索引库的名称
    },
}
# 当添加、修改、删除数据时，自动生成索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# Haystack 分页每页结果数量
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5

# 支付功能对接alipay配置
ALIPAY_APPID = "2021000117610712"
ALIPAY_DEBUG = True
ALIPAY_URL = "https://openapi.alipaydev.com/gateway.do"
ALIPAY_RETURN_URL = "http://127.0.0.1:8000/payment/status/"

# 定时器配置
CRONJOBS = [
    # 每1分钟生成一次首页静态文件
    ('*/1 * * * *', 'contents.crons.generate_static_index_html',
     '>> ' + os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log'))
]
# 解决crontab中文问题
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'

# CORS 解决跨域问题
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://127.0.0.1:8000',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000'
)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

# Django REST Framework configurations
REST_FRAMEWORK = {
    # 指定认证方式
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # JWT
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

# JWT configurations
JWT_AUTH = {
    # 指定有效期
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 重写返回结果方法
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'meiduo_admin.utils.jwt_response_payload_handler',
}
