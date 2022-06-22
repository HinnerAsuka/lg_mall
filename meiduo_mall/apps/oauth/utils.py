from authlib.jose import jwt, JoseError
from meiduo_mall import settings


# 加密
def generic_openid(openid):
    # 签名算法
    header = {'alg': 'HS512'}
    key = settings.SECRET_KEY
    data = {'openid': openid}
    access_token = jwt.encode(header=header, payload=data, key=key)

    # 将bytes类型转换为str
    return access_token.decode()


# 解密
def check_access_token(token):
    key = settings.SECRET_KEY
    try:
        result = jwt.decode(token, key)
    except JoseError:
        return False
    return result.get('openid')
