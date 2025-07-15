import os

# Database settings fix
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME', 'tictactoe_db'),
        'USER': os.environ.get('DATABASE_USER', 'root'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'Root23175@'),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '3306'),
    }
}

# Configure Redis for channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://redis:6379/1')],
        },
    }
}