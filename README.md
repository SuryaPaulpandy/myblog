# 🚀 MyBlog - Modern Django Blog Platform

A full-featured, modern blog platform built with Django that provides a seamless content creation and management experience. This project showcases advanced web development skills with authentication, CRUD operations, image handling, and a beautiful responsive UI.

![Django](https://img.shields.io/badge/Django-5.2-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

## ✨ Features

### 🔐 Authentication & Security
- **Dual Login System**: Traditional username/password and OTP-based email login
- **Password Reset**: Secure password reset via email with token-based authentication
- **Session Management**: Configurable session timeout and security
- **Permission-Based Access**: Role-based permissions for post management

### 📝 Content Management
- **Rich Post Creation**: Create posts with title, category, content, and images
- **Image Handling**: Support for both uploaded images and online image URLs
- **Category System**: Organize posts by categories (Technology, Science, Art, Sports, Food)
- **Draft & Publish**: Save drafts and publish when ready
- **Edit & Delete**: Full CRUD operations for posts

### 🎨 User Experience
- **Responsive Design**: Beautiful, modern UI that works on all devices
- **Dashboard Analytics**: View total posts, published posts, and drafts
- **Save/Bookmark Posts**: Save favorite posts for later reading
- **Category Filtering**: Filter posts by category
- **Pagination**: Efficient pagination for better performance
- **Search & Navigation**: Easy navigation and content discovery

### 📧 Communication
- **Newsletter Subscription**: Email subscription system
- **Contact Form**: Direct contact form with email notifications
- **Email Notifications**: Automated emails for password reset and OTP

### 🎯 Additional Features
- **User Profiles**: Customizable user profiles
- **About Page**: Dynamic about page content
- **SEO Optimized**: Meta tags and descriptions for better search visibility
- **Modern UI/UX**: Glassmorphism effects, smooth animations, and gradient designs

## 🛠️ Tech Stack

- **Backend**: Django 5.2
- **Database**: MySQL 8.0
- **Frontend**: Bootstrap 5.3, HTML5, CSS3, JavaScript
- **Icons**: Bootstrap Icons
- **Animations**: Animate.css
- **Image Processing**: Pillow
- **Email**: SMTP (Gmail)

## 📋 Prerequisites

- Python 3.11+
- MySQL 8.0+
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/myblog.git
cd myblog
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
- Create a MySQL database named `blog`
- Update database credentials in `MyApp/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'blog',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Categories
```bash
python manage.py populate_categories
```

### 7. Create Admin User & Sample Posts (Optional)
```bash
python manage.py create_admin_posts
```
This creates:
- Admin user: `Surya` / Password: `12345678`
- 30 sample posts with images

### 8. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

## 📁 Project Structure

```
myblog/
├── MyApp/              # Main Django project settings
│   ├── settings.py     # Project configuration
│   ├── urls.py        # Main URL routing
│   └── middleware.py  # Custom middleware
├── blog/              # Blog application
│   ├── models.py     # Database models
│   ├── views.py      # View functions
│   ├── urls.py       # App URL routing
│   ├── forms.py      # Django forms
│   ├── admin.py      # Admin configuration
│   ├── templates/    # HTML templates
│   ├── static/       # Static files (CSS, JS, images)
│   └── management/   # Management commands
├── media/            # User-uploaded files
├── templates/        # Global templates
└── requirements.txt  # Python dependencies
```

## 🎯 Key Features Implementation

### Authentication Flow
- User registration with email verification
- Dual login options (password/OTP)
- Secure password reset with time-limited tokens
- Session-based authentication with configurable timeout

### Post Management
- Image upload with automatic optimization
- Slug generation for SEO-friendly URLs
- Category-based organization
- Draft and publish workflow
- User-specific post management

### UI/UX Highlights
- Modern gradient designs
- Smooth animations and transitions
- Responsive card layouts
- Glassmorphism effects
- Interactive hover states

## 🔧 Management Commands

### Create Categories
```bash
python manage.py populate_categories
```

### Create Sample Posts
```bash
python manage.py populate_posts
```

### Create Admin User & Posts
```bash
python manage.py create_admin_posts
```

## 📸 Screenshots

### Homepage
- Modern hero section with gradient background
- Category-based post filtering
- Responsive card grid layout

### Dashboard
- Post statistics (Total, Published, Drafts)
- Quick actions sidebar
- Post management interface

### Post Creation
- Rich form with image upload
- Category selection
- Content editor

## 🌐 Live Demo

[Add your live demo URL here]

## 👨‍💻 Author

**Surya**
- Portfolio: [https://surya-portfolio.netlify.app/](https://surya-portfolio.netlify.app/)
- LinkedIn: [https://linkedin.com/in/surya-p-03950722a/](https://linkedin.com/in/surya-p-03950722a/)
- Instagram: [@surya__bae](https://www.instagram.com/surya__bae/)

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Django Documentation
- Bootstrap Team
- All open-source contributors

## 📈 Future Enhancements

- [ ] Comment system
- [ ] Like/Dislike functionality
- [ ] Advanced search
- [ ] Tag system
- [ ] Social media sharing
- [ ] Analytics dashboard
- [ ] API endpoints
- [ ] Multi-language support

---

⭐ If you like this project, give it a star on GitHub!
