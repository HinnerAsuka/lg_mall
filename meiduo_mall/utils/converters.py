from django.urls import converters


# 自定义转换器

class UsernameConverter:
    regex = '[a-zA-Z0-9_-]{5,20}'

    def to_python(self, value):
        return value


class MobileConverter:
    regex = '1[3-9]\d{9}'

    def to_python(self, value):
        return value
