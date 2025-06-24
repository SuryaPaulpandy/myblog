"""Django Forms Modules"""

import random

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from blog.models import Category, Post


from django.core.validators import RegexValidator


class RegisterForm(forms.ModelForm):
    """This is a registerform"""

    username = forms.CharField(label="username", max_length=100, required=True)
    email = forms.CharField(label="email", max_length=100, required=True)
    password = forms.CharField(label="password", max_length=100, required=True)
    password_confirm = forms.CharField(
        label="password confirm", max_length=100, required=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")


class ResetPasswordForm(forms.Form):
    """This is ResetPasswordForm"""

    new_password = forms.CharField(label="New Password", min_length=8)
    confirm_password = forms.CharField(label="Confirm Password", min_length=8)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")


class PostForm(forms.ModelForm):
    """This is a NewPostForm"""

    title = forms.CharField(label="Title", max_length=200, required=True)
    content = forms.CharField(label="Content", required=True)
    category = forms.ModelChoiceField(
        label="Category", required=True, queryset=Category.objects.all()
    )
    img_url = forms.ImageField(label="Image", required=False)

    class Meta:
        model = Post
        fields = ["title", "content", "category", "img_url"]

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        content = cleaned_data.get("content")

        # custom validation
        if title and len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 Characters long.")

        if content and len(content) < 10:
            raise forms.ValidationError("Content must be at least 10 Characters long.")

    def save(self, commit=...):

        post = super().save(commit)
        cleaned_data = super().clean()

        if cleaned_data.get("img_url"):
            post.img_url = cleaned_data.get("img_url")
        else:
            img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"
            post.img_url = img_url

        if commit:
            post.save()
        return post


User = get_user_model()


# class LoginForm(forms.Form):
#     """Existing password login form"""

#     username = forms.CharField(label="Username", max_length=100, required=True)
#     password = forms.CharField(label="Password", max_length=100, required=True)


# class EmailLoginForm(forms.Form):
#     """Form for email-based OTP login"""

#     email = forms.EmailField(label="Email", required=True)

#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         if not User.objects.filter(email=email).exists():
#             raise ValidationError("No account found with this email address.")
#         return email


# class VerifyOTPForm(forms.Form):
#     """Form for OTP verification"""

#     otp = forms.CharField(
#         label="OTP",
#         max_length=6,
#         min_length=6,
#         required=True,
#         widget=forms.TextInput(
#             attrs={"placeholder": "Enter 6-digit code", "class": "form-control"}
#         ),
#     )
#     email = forms.EmailField(widget=forms.HiddenInput())

#     def clean_otp(self):
#         otp = self.cleaned_data.get("otp")
#         if not otp.isdigit():
#             raise forms.ValidationError("OTP must contain only numbers")
#         return otp


# class VerifyOTPForm(forms.Form):
#     otp = forms.CharField(
#         label="OTP Code",
#         max_length=6,
#         min_length=6,
#         widget=forms.TextInput(
#             attrs={"placeholder": "Enter 6-digit code", "class": "form-control"}
#         ),
#         validators=[RegexValidator(regex="^[0-9]{6}$", message="OTP must be 6 digits")],
#     )
#     email = forms.EmailField(widget=forms.HiddenInput())


User = get_user_model()


class ForgotPasswordForm(forms.Form):
    """Improved forgot password form with better validation"""

    email = forms.EmailField(
        label="Email",
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "Enter your email address", "class": "form-control"}
        ),
    )

    def clean_email(self):
        """Validate that email exists in system"""
        email = self.cleaned_data.get("email").lower().strip()

        if not User.objects.filter(email__iexact=email).exists():
            raise ValidationError("No account found with this email address.")

        return email


from django import forms
from django.core.validators import RegexValidator, validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from blog.models import Category, Post

User = get_user_model()


class LoginForm(forms.Form):
    """Traditional username/password login form"""

    username = forms.CharField(
        label="Username",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Password",
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )


class EmailLoginForm(forms.Form):
    """Form for email-based OTP login"""

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account found with this email address.")
        return email


class OTPVerificationForm(forms.Form):
    """Form for OTP verification"""

    otp = forms.CharField(
        label="OTP",
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter 6-digit code"}
        ),
        validators=[RegexValidator(regex="^[0-9]{6}$", message="OTP must be 6 digits")],
    )
    """Form for OTP verification"""
    otp = forms.CharField(
        label="OTP Code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter 6-digit OTP",
                "pattern": r"\d{6}",
                "inputmode": "numeric",
            }
        ),
        validators=[RegexValidator(regex="^[0-9]{6}$", message="OTP must be 6 digits")],
        error_messages={
            "required": "OTP is required",
            "min_length": "OTP must be 6 digits",
            "max_length": "OTP must be 6 digits",
        },
    )
