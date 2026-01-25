"""Django Views for Blog App"""

import logging
import random
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import (
    ForgotPasswordForm,
    PostForm,
    RegisterForm,
    ResetPasswordForm,
    LoginForm,
    EmailLoginForm,
    OTPVerificationForm,
    EditProfileForm,
    SubscribeForm,
)
from .models import AboutUs, Category, Post, Subscriber

logger = logging.getLogger(__name__)
User = get_user_model()


def index(request):
    """Display all blog posts on the index page."""
    blog_title = "Latest Posts"
    all_posts = Post.objects.filter(is_published=True).order_by('-created_at')  # Newest first
    categories = Category.objects.all()

    category_name = request.GET.get("category")
    if category_name:
        all_posts = all_posts.filter(category__name=category_name)
        blog_title = f"{category_name} Posts"

    # Calculate statistics for homepage
    total_posts = Post.objects.filter(is_published=True).count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()
    recent_posts_count = Post.objects.filter(is_published=True).order_by('-created_at')[:5].count()

    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Calculate elided page range for pagination
    custom_range = page_obj.paginator.get_elided_page_range(
        page_obj.number, 
        on_each_side=1, 
        on_ends=1
    )
    
    return render(
        request, 
        "blog/index.html", 
        {
            "blog_title": blog_title, 
            "page_obj": page_obj,
            "paginator": paginator,
            "categories": categories,
            "current_category": category_name,
            "custom_range": custom_range,
            "total_posts": total_posts,
            "total_categories": total_categories,
            "total_users": total_users,
            "recent_posts_count": recent_posts_count,
        }
    )

def detail(request, slug):
    """Display the detail page of a specific blog post using the slug."""

    if not request.user.is_authenticated:
        messages.info(request, "Please sign in")
        return redirect("blog:login")

    if not request.user.has_perm("blog.view_post"):
        messages.error(request, "You have no permission to view any posts")
        return redirect("blog:index")
    post = get_object_or_404(Post, slug=slug)
    related_posts = Post.objects.filter(category=post.category).exclude(pk=post.id)
    return render(
        request, "blog/detail.html", {"post": post, "related_posts": related_posts}
    )


def old_url_redirect(request):
    """Redirect from an old URL to the new detail page."""
    return redirect(reverse("blog:new_page_url"))


def new_url_view(request):
    """Display a simple message for the new URL."""
    return HttpResponse("This is the new URL.")


def contact(request):
    """Handle contact form submission and send email to the client."""

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        logger = logging.getLogger("TESTING")
        logger.debug(
            "Received POST data: Name: %s, Email: %s, Message: %s", name, email, message
        )

        if name and email and message:

            full_message = f"""You have a new contact form submission:

            Name: {name}
            Email: {email}
            Message:
            {message}
            """

            send_mail(
                subject=f"Contact Form Submission from {name}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )

            success_message = "Your Email has been sent!"
            return render(
                request,
                "blog/contact.html",
                {
                    "success_message": success_message,
                    # "name": name,
                    # "email": email,
                    # "message": message,
                },
            )

        else:

            error_message = "All fields are required."
            return render(
                request,
                "blog/contact.html",
                {
                    "error_message": error_message,
                    "name": name,
                    "email": email,
                    "message": message,
                },
            )

    return render(request, "blog/contact.html")


def about(request):
    """To Get a About Page"""
    about_content = AboutUs.objects.first()
    if about_content is None or not about_content.content:
        about_content = "Default content goes here."
    else:
        about_content = about_content.content

    return render(request, "blog/about.html", {"about_content": about_content})


def register(request):
    """To get a register page"""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            readers_group, created = Group.objects.get_or_create(name="Readers")
            user.groups.add(readers_group)

            messages.success(request, "Registration successful! You can now log in.")
            return redirect("blog:login")
    else:
        form = RegisterForm()
    return render(request, "blog/register.html", {"form": form})



# ... (rest of the file content is mostly fine, just removing the redundant User definition lines)

@login_required
def dashboard(request):
    """To get a dashboard page"""
    blog_title = "My Posts"

    username = request.session.get("username", "Guest")
    is_logged_in = request.session.get("is_logged_in", False)

    # Only show posts created by the current user, ordered by newest first
    all_posts = Post.objects.filter(user=request.user).order_by('-created_at')

    # Calculate statistics (before filtering the list)
    total_posts = all_posts.count()
    published_posts = all_posts.filter(is_published=True).count()
    draft_posts = all_posts.filter(is_published=False).count()

    # Apply filters
    filter_type = request.GET.get("filter")
    if filter_type == "published":
        all_posts = all_posts.filter(is_published=True)
    elif filter_type == "drafts":
        all_posts = all_posts.filter(is_published=False)

    # Check for sections (e.g. Saved Items)
    section = request.GET.get('section')
    if section == 'saved':
        all_posts = request.user.saved_posts.all()
        blog_title = "Saved Items"

    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Use elided page range for cleaner, consistent pagination UI
    custom_range = page_obj.paginator.get_elided_page_range(
        page_obj.number, on_each_side=1, on_ends=1
    )

    return render(
        request,
        "blog/dashboard.html",
        {
            "blog_title": blog_title,
            "page_obj": page_obj,
            "custom_range": custom_range,
            "username": username,
            "is_logged_in": is_logged_in,
            "total_posts": total_posts,
            "published_posts": published_posts,
            "draft_posts": draft_posts,
            "current_filter": filter_type,
            "current_section": section,
        },
    )


def logout(request):
    """To get a logout page"""
    auth_logout(request)
    request.session.flush()
    return redirect("blog:index")



def forgot_password(request):
    """Handle forgot password requests with improved error handling"""
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)

                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Get current site domain
                current_site = get_current_site(request)
                domain = current_site.domain

                # Save reset info in session
                request.session["reset_start_time"] = timezone.now().isoformat()
                request.session["reset_user_id"] = user.pk
                request.session["reset_email"] = email  # Store email for verification

                # Prepare email
                subject = "Password Reset Request"
                message = render_to_string(
                    "blog/reset_password_email.html",
                    {
                        "user": user,
                        "domain": domain,
                        "uid": uid,
                        "token": token,
                    },
                )

                # Send email
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # Use from settings
                    [email],
                    fail_silently=False,
                )

                messages.success(
                    request, "Password reset link has been sent to your email."
                )
                return redirect("blog:login")

            except User.DoesNotExist:
                # This shouldn't happen due to form validation, but just in case
                messages.error(request, "No user found with this email address.")
            except Exception as e:
                logger.error(f"Error sending password reset email: {str(e)}")
                messages.error(
                    request,
                    "An error occurred while sending the reset email. Please try again later.",
                )
    else:
        form = ForgotPasswordForm()

    return render(request, "blog/forgot_password.html", {"form": form})


def reset_password(request, uidb64, token):
    """To get a rest_password page views"""
    form = ResetPasswordForm()

    #  Check if 5 minutes passed
    reset_time = request.session.get("reset_start_time")
    if reset_time:
        reset_time = timezone.datetime.fromisoformat(reset_time)
        now = timezone.now()

        if now - reset_time > timedelta(minutes=5):
            messages.error(request, "Reset link has expired. Please request a new one.")
            return redirect("blog:forgot_password")

    if request.method == "POST":

        # If session expired, redirect
        if not request.session.exists(request.session.session_key):
            messages.error(request, "Session expired. Please try again.")
            return redirect("blog:forgot_password")

        # form
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            try:
                uid = urlsafe_base64_decode(uidb64)
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully!")
                request.session.pop("reset_password_active", None)  # clear session key
                return redirect("blog:login")
            else:
                messages.error(request, "The password reset link is invalid")

    return render(request, "blog/reset_password.html", {"form": form})


@login_required
def new_post(request):
    """To get a new_post page - Available to ALL logged-in users"""
    # No permission check - any logged-in user can create posts
    categories = Category.objects.all()
    form = PostForm()
    if request.method == "POST":
        # form
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            
            # Handle image: Priority - Uploaded file > URL input > Default category image
            image_url_input = form.cleaned_data.get("image_url_input")
            img_file = form.cleaned_data.get("img_url")
            
            if img_file:
                # User uploaded a file - use it directly, clear online URL
                post.img_url = img_file
                post.image_url_online = None  # Clear online URL if file is uploaded
            elif image_url_input:
                # User provided URL - validate it's an image and store URL directly (don't download)
                try:
                    import urllib.request
                    
                    # Validate URL is an image (HEAD request to check content-type)
                    req_head = urllib.request.Request(image_url_input, method='HEAD')
                    req_head.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                    
                    try:
                        with urllib.request.urlopen(req_head, timeout=10) as head_response:
                            content_type = head_response.headers.get('Content-Type', '').lower()
                            
                            # Validate it's an image
                            if not any(img_type in content_type for img_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/svg']):
                                # Check if it's a video
                                if 'video' in content_type:
                                    messages.error(request, "Please upload correct URL for images only. Videos are not allowed. Allowed formats: JPG, PNG, GIF, WEBP, etc.")
                                    return render(request, "blog/new_post.html", {"categories": categories, "form": form})
                                elif 'text/html' in content_type or 'html' in content_type:
                                    messages.error(request, "This is a webpage URL, not a direct image URL. Please use a direct image URL (e.g., https://example.com/image.jpg). For Freepik images, right-click the image and select 'Copy image address' to get the direct URL.")
                                    return render(request, "blog/new_post.html", {"categories": categories, "form": form})
                                else:
                                    messages.error(request, f"Please upload correct URL for images only. The URL returned: {content_type}. Allowed formats: JPG, PNG, GIF, WEBP, etc. Make sure you're using a direct image URL, not a webpage URL.")
                                    return render(request, "blog/new_post.html", {"categories": categories, "form": form})
                    except Exception as e:
                        # HEAD request failed - check if URL looks like a webpage
                        if any(domain in image_url_input.lower() for domain in ['freepik.com', 'unsplash.com/photos', 'pexels.com/photo', 'pinterest.com', '.htm', '.html']):
                            messages.error(request, "This appears to be a webpage URL, not a direct image URL. Please use a direct image URL. Right-click on the image and select 'Copy image address' or 'Copy image URL' to get the direct link.")
                            return render(request, "blog/new_post.html", {"categories": categories, "form": form})
                        # Otherwise, accept the URL (might be CORS issues or valid image URL)
                        pass
                    
                    # Store the URL directly (don't download)
                    post.image_url_online = image_url_input
                    post.img_url = None  # Clear uploaded file if URL is provided
                    
                except urllib.error.HTTPError as e:
                    messages.error(request, f"Could not access the URL. Error: {e.code} {e.reason}. Please check the URL and try again.")
                    return render(request, "blog/new_post.html", {"categories": categories, "form": form})
                except urllib.error.URLError as e:
                    messages.error(request, f"Invalid URL or network error: {str(e)}. Please check the URL and try again.")
                    return render(request, "blog/new_post.html", {"categories": categories, "form": form})
                except Exception as e:
                    messages.error(request, f"Error validating image URL: {str(e)}. Please check the URL and try again.")
                    return render(request, "blog/new_post.html", {"categories": categories, "form": form})
            
            # Save the post (always save, regardless of image)
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect("blog:dashboard")
    return render(
        request, "blog/new_post.html", {"categories": categories, "form": form}
    )


@login_required
@login_required
def edit_post(request, post_id):
    """To get aedit_post views"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check ownership
    if post.user != request.user:
        messages.error(request, "You are not authorized to edit this post")
        return redirect("blog:dashboard")
        
    categories = Category.objects.all()
    form = PostForm(instance=post)  # Initialize form with instance for GET request
    
    if request.method == "POST":
        # form
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            # Get the updated post instance
            updated_post = form.save(commit=False)
            
            # Handle image updates: Priority - Uploaded file > URL input > Keep existing
            image_url_input = form.cleaned_data.get("image_url_input")
            img_file = form.cleaned_data.get("img_url")
            
            if img_file:
                # User uploaded a new file - delete old file first, then save new one
                # Delete old image file if it exists
                if post.img_url:
                    try:
                        import os
                        from django.conf import settings
                        old_file_path = post.img_url.path if hasattr(post.img_url, 'path') else None
                        if old_file_path and os.path.exists(old_file_path):
                            os.remove(old_file_path)
                    except Exception as e:
                        # If deletion fails, continue anyway
                        pass
                
                # Save new uploaded file
                updated_post.img_url = img_file
                updated_post.image_url_online = None  # Clear online URL if file is uploaded
            elif image_url_input:
                # User provided new URL - validate it's an image and store URL directly
                try:
                    import urllib.request
                    
                    # Validate URL is an image (HEAD request to check content-type)
                    req_head = urllib.request.Request(image_url_input, method='HEAD')
                    req_head.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                    
                    try:
                        with urllib.request.urlopen(req_head, timeout=10) as head_response:
                            content_type = head_response.headers.get('Content-Type', '').lower()
                            
                            # Validate it's an image
                            if not any(img_type in content_type for img_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/svg']):
                                # Check if it's a video
                                if 'video' in content_type:
                                    messages.error(request, "Please upload correct URL for images only. Videos are not allowed. Allowed formats: JPG, PNG, GIF, WEBP, etc.")
                                    return render(request, "blog/edit_post.html", {"categories": categories, "post": post, "form": form})
                                elif 'text/html' in content_type or 'html' in content_type:
                                    messages.error(request, "This is a webpage URL, not a direct image URL. Please use a direct image URL (e.g., https://example.com/image.jpg). For Freepik images, right-click the image and select 'Copy image address' to get the direct URL.")
                                    return render(request, "blog/edit_post.html", {"categories": categories, "post": post, "form": form})
                                else:
                                    messages.error(request, f"Please upload correct URL for images only. The URL returned: {content_type}. Allowed formats: JPG, PNG, GIF, WEBP, etc. Make sure you're using a direct image URL, not a webpage URL.")
                                    return render(request, "blog/edit_post.html", {"categories": categories, "post": post, "form": form})
                    except Exception as e:
                        # HEAD request failed - check if URL looks like a webpage
                        if any(domain in image_url_input.lower() for domain in ['freepik.com', 'unsplash.com/photos', 'pexels.com/photo', 'pinterest.com', '.htm', '.html']):
                            messages.error(request, "This appears to be a webpage URL, not a direct image URL. Please use a direct image URL. Right-click on the image and select 'Copy image address' or 'Copy image URL' to get the direct link.")
                            return render(request, "blog/edit_post.html", {"categories": categories, "post": post, "form": form})
                        # Otherwise, accept the URL (might be CORS issues or valid image URL)
                        pass
                    
                    # Store the new URL directly (don't download)
                    updated_post.image_url_online = image_url_input
                    updated_post.img_url = None  # Clear uploaded file if URL is provided
                    
                except urllib.error.HTTPError as e:
                    messages.error(request, f"Could not access the URL. Error: {e.code} {e.reason}. Please check the URL and try again.")
                    return render(request, "blog/edit_post.html", {"categories": categories, "post": post, "form": form})
                except urllib.error.URLError as e:
                    messages.error(request, f"Invalid URL or network error: {str(e)}. Please check the URL and try again.")
                    return render(request, "blog/edit_post.html", {"categories": categories, "post": post, "form": form})
                except Exception as e:
                    messages.error(request, f"Error validating image URL: {str(e)}. Please check the URL and try again.")
                    return render(request, "blog/edit_post.html", {"categories": categories, "post": post, "form": form})
            # If no new image provided, keep existing image (don't change it)
            
            # Save the updated post
            updated_post.save()
            messages.success(request, "Post Updated Succesfully!")
            return redirect("blog:dashboard")

    return render(
        request,
        "blog/edit_post.html",
        {"categories": categories, "post": post, "form": form},
    )


@login_required
@login_required
def delete_post(request, post_id):
    """To get a delete_post views"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check ownership
    if post.user != request.user:
        messages.error(request, "You are not authorized to delete this post")
        return redirect("blog:dashboard")
        
    post.delete()
    messages.success(request, "Post Deleted Succesfully!")
    return redirect("blog:dashboard")


@login_required
@login_required
def publish_post(request, post_id):
    """To get a published_post views"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check ownership
    if post.user != request.user:
        messages.error(request, "You are not authorized to publish this post")
        return redirect("blog:dashboard")
        
    post.is_published = True
    post.save()
    messages.success(request, "Post Published Succesfully!")
    return redirect("blog:dashboard")


def login(request):
    """Handle both traditional and OTP login"""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect("blog:dashboard")
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "blog/login.html", {"form": form})


def email_login(request):
    """Initiate OTP login process"""
    if request.method == "POST":
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            otp = str(random.randint(100000, 999999))
            expiry_time = timezone.now() + timedelta(minutes=3)

            # Store OTP in session
            request.session["otp_data"] = {
                "otp": otp,
                "expiry": expiry_time.isoformat(),
                "email": email,
            }

            # Send OTP email
            send_mail(
                "Your Login OTP",
                f"Your OTP code is: {otp}\n\nThis code will expire in 3 minutes.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, "OTP has been sent to your email!")
            return redirect("blog:verify_otp")
    else:
        form = EmailLoginForm()

    return render(request, "blog/email_login.html", {"form": form})


def verify_otp(request):
    """Verify the OTP entered by user"""
    otp_data = request.session.get("otp_data")
    if not otp_data:
        messages.error(request, "Session expired. Please request a new OTP.")
        return redirect("blog:email_login")

    email = otp_data["email"]
    expiry_time = datetime.fromisoformat(otp_data["expiry"])

    if request.method == "POST":
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            user_otp = form.cleaned_data["otp"]

            # Check if OTP expired
            if timezone.now() > expiry_time:
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect("blog:email_login")

            # Verify OTP
            if user_otp == otp_data["otp"]:
                user = User.objects.filter(email=email).first()
                auth_login(request, user)
                del request.session["otp_data"]
                messages.success(request, "Logged in successfully!")
                return redirect("blog:dashboard")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
    else:
        form = OTPVerificationForm()

    # Calculate remaining time in seconds
    remaining_seconds = max(0, int((expiry_time - timezone.now()).total_seconds()))

    return render(
        request,
        "blog/verify_otp.html",
        {
            "form": form,
            "email": email,
            "remaining_seconds": remaining_seconds,
            "otp_expiry": otp_data["expiry"],
        },
    )



def resend_otp(request):
    """Handle OTP resend requests"""
    if request.method == "POST":
        otp_data = request.session.get("otp_data")
        if not otp_data:
            return JsonResponse({"success": False, "error": "Session expired"})

        email = otp_data["email"]
        new_otp = str(random.randint(100000, 999999))
        expiry_time = timezone.now() + timedelta(minutes=3)

        # Update session with new OTP
        request.session["otp_data"] = {
            "otp": new_otp,
            "expiry": expiry_time.isoformat(),
            "email": email,
        }

        # Send new OTP email
        send_mail(
            "Your New Login OTP",
            f"Your new OTP code is: {new_otp}\n\nThis code will expire in 3 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "New OTP sent successfully",
                "new_expiry": expiry_time.isoformat(),
            }
        )

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def profile(request):
    """Display user profile"""
    return render(request, "blog/profile.html", {"user": request.user})


@login_required
def edit_profile(request):
    """View to edit user profile"""
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile looks amazing!')
            return redirect('blog:profile')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'blog/edit_profile.html', {'form': form})


def subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            Subscriber.objects.create(email=email)
            messages.success(request, 'Successfully subscribed to the newsletter!')
        else:
            # If checking directly on index/detail might be tricky to render errors inline 
            # without full context, often better to just flash message or simple redirect.
            # For simplicity, we'll flash the first error.
            if form.errors:
                key, error_list = list(form.errors.items())[0]
                messages.error(request, error_list[0])
            
    # Redirect back to where the user came from, or home
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


@login_required
def toggle_save_post(request, post_id):
    """Save or unsave a post"""
    post = get_object_or_404(Post, id=post_id)
    if post.saved_by.filter(id=request.user.id).exists():
        post.saved_by.remove(request.user)
        messages.success(request, 'Post removed from saved items.')
    else:
        post.saved_by.add(request.user)
        messages.success(request, 'Post saved successfully.')
    
    return redirect('blog:detail', slug=post.slug)
