from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib.messages import add_message
from django.contrib import auth


# Criação dos endpoints

# Cadastro
def cadastro(request):
    if request.method == "GET":
        return render(request, "cadastro.html")    
    
    if len(request.POST.get('senha')) < 8:
        add_message(request, constants.ERROR, "A senha deve ser maior que 8 caracteres.")

    if  request.POST.get('senha') != request.POST.get('confirmar_senha'):
        add_message(request, constants.ERROR, "A senha e a confirmação devem ser iguais.")
        return redirect('/usuarios/cadastro')
    
    users = User.objects.filter(username=request.POST.get('username'))

    if users.exists():
        add_message(request, constants.ERROR, "Usuário já cadastrado.")
        return redirect('/usuarios/cadastro')
    
    try:
        user = User.objects.create_user(
            username = request.POST.get('username'),            
            password = request.POST.get('senha'))
        return redirect("/usuarios/login")
    except:
        return redirect('/usuarios/cadastro')

# Login
def logar(request):
    if request.method == "GET":
        return render(request, 'logar.html')
    elif request.method == "POST":
         user = auth.authenticate(request, 
            username = request.POST.get('username'), 
            password = request.POST.get('senha'))
         if user:
             auth.login(request, user)
             return redirect('/usuarios/home')         
         add_message(request, constants.ERROR, "Usuário ou senha não conferem.")
         return redirect("/usuarios/logar")

# Logout
def logout(request):
    auth.logout(request)
    return redirect("/usuarios/logar")