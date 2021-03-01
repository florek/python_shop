from django import forms


class CouponApplyForm(forms.Form):
    coupon = forms.CharField()
