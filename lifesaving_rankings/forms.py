from allauth.account.forms import SignupForm
from hcaptcha.fields import hCaptchaField


class CaptchaSignupForm(SignupForm):
    hcaptcha = hCaptchaField()
    field_order = ['username', 'email', 'password1', 'password2', 'hcaptcha']

    def save(self, request):
        return super(CaptchaSignupForm, self).save(request)
