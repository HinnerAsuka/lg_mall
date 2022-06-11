from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.http import JsonResponse

# 方法一
# class LoginRequiredJSONMixin(AccessMixin):
#     """Verify that the current user is authenticated."""
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'code': 400, 'errmsg': '没有登陆'})
#         return super().dispatch(request, *args, **kwargs)


# 方法二：重写函数方法实现用户未登录的JSON数据
class LoginRequiredJSONMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return JsonResponse({'code': 400, 'errmsg': '没有登陆'})