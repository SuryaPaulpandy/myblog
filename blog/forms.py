"""Django Forms Modules"""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from blog.models import Category, Post, Subscriber

User = get_user_model()


class RegisterForm(forms.ModelForm):
    """This is a registerform"""

    username = forms.CharField(label="Username", max_length=100, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="Email", max_length=100, required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Password", max_length=100, required=True, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password_confirm = forms.CharField(
        label="Confirm Password", max_length=100, required=True, widget=forms.PasswordInput(attrs={"class": "form-control"})
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

    new_password = forms.CharField(label="New Password", min_length=8, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    confirm_password = forms.CharField(label="Confirm Password", min_length=8, widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")


class PostForm(forms.ModelForm):
    """This is a NewPostForm"""

    title = forms.CharField(label="Title", max_length=200, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    content = forms.CharField(label="Content", required=True, widget=forms.Textarea(attrs={"class": "form-control", "rows": 5}))
    category = forms.ModelChoiceField(
        label="Category", required=True, queryset=Category.objects.all(), widget=forms.Select(attrs={"class": "form-select"})
    )
    img_url = forms.ImageField(label="Image", required=False, widget=forms.FileInput(attrs={"class": "form-control"}))

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

    def save(self, commit=True):
        post = super().save(commit=False)
        # Image handling is done in the view
        if commit:
            post.save()
        return post


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


class EditProfileForm(forms.ModelForm):
    """Form to edit user profile details"""
    
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already currently used.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This username is already taken.')
        return username


class SubscribeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}), label='')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Subscriber.objects.filter(email=email).exists():
            raise forms.ValidationError('You are already subscribed!')
        return email
