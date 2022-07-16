from django.core.files.storage import Storage


class MyStorage(Storage):

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass

    def exists(self, name):
        # 判断图片是否存在
        # fastdfs会自动处理图片重名
        # 返回False，说明图片不存在，进行上传
        return False

    def url(self, name):
        return 'http://192.168.146.130:8888/' + name