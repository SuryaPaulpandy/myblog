"""Django Modules"""

from django.shortcuts import render


def custom_page_not_found(request, exception):
    """This is page Not Found"""
    return render(request, "404.html", status=404)
