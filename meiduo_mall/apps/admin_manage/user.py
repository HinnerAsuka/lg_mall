from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings


def jwt_response_payload_handler(token, user, request):
    return {
        'token': token,
        'username': user.username,
        'id': user.id
    }


from rest_framework_jwt.serializers import JSONWebTokenSerializer
from django.utils.translation import ugettext as _

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


# 重写登录判断
class LegouWebTokenSerializer(JSONWebTokenSerializer):

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                # 添加判断用户是否为管理员
                if not user.is_staff:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


from rest_framework_jwt.views import JSONWebTokenAPIView


# 重写
class LegouObtainJSONWebToken(JSONWebTokenAPIView):
    serializer_class = LegouWebTokenSerializer


legou_jwt_token = LegouObtainJSONWebToken.as_view()
