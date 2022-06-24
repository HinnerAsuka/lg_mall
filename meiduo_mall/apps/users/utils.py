from authlib.jose import jwt, JoseError
from meiduo_mall import settings


# 对用户id进行加密
def generic_email_verify_token(user_id):
    header = {'alg': 'HS512'}
    key = settings.SECRET_KEY
    data = {'user_id': user_id}
    access_token = jwt.encode(header=header, payload=data, key=key)
    return access_token.decode()


# 解密
def check_verify_token(token):
    key = settings.SECRET_KEY
    try:
        result = jwt.decode(token, key)
    except JoseError:
        return False
    return result.get('user_id')
