from django import http

def home(request):
    return http.HttpResponse("Hello, world. You're at the core index.")
