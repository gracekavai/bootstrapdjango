from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect, render

from myapp.forms import ContactForm


def index(request):
    return render(request, 'myapp/index.html')

def about(request):
    return render(request, 'myapp/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Submitted. Please await feedback.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'myapp/contact.html', {'form': form})

def properties(request):
    return render(request, 'myapp/properties.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'myapp/register.html', {'form': form})