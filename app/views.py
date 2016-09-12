#!-*- conding: utf8 -*-
from __future__ import print_function
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from .models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.core.files.base import ContentFile
import re

def index(request):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        return redirect('/app')
    except:
        return render_to_response('login.html', {}, context_instance=RequestContext(request))


# Falta criar o template register.html
# Falta exportar base.html
def registro(request):
    if request.method == 'GET':
        return render_to_response('registro.html', {}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        senha = request.POST['senha']
        confirmacao_senha = request.POST['confirmacao_senha']

        if senha != confirmacao_senha:
            messages.error(request, 'Senhas nao coincidem')
            return render_to_response('registro.html', {}, context_instance=RequestContext(request))

        try:
            us_temp = Usuario.objects.get(email=email)
            messages.error(request, 'Email ja cadastrado')

            return render_to_response('registro.html', {}, context_instance=RequestContext(request))

        except:
            try:
                name_temp = Usuario.objects.get(nome=nome)
                messages.error(request, 'Nome de usuario ja cadastrado')
                return render_to_response('registro.html', {}, context_instance=RequestContext(request))
            except:
                new_usuario = Usuario(nome=nome, email=email, senha=senha)
                new_usuario.save()
                messages.success(request, 'Usuario criado com sucesso')
                return redirect('/')


def login(request):
    if request.method == 'GET':
        return redirect('/')
    elif request.method == 'POST':
        nome_ou_email = request.POST['nome_ou_email']
        senha = request.POST['senha']
        PADRAO_EMAIL = re.compile(r"^[A-Za-z0-9-_]+\.?[A-Za-z0-9-_]+?@[A-Za-z0-9-]+\.[A-Za-z0-9-]+?\.?[A-Za-z0-9-]+?\.?[A-Za-z0-9-]+?")
        PADRAO_NOME = re.compile(r"[A-Z]?[A-Za-z0-9]{4,100}")

        try:
            if PADRAO_EMAIL.match(nome_ou_email):
                usuario = Usuario.objects.get(email=nome_ou_email)
            elif PADRAO_NOME.match(nome_ou_email):
                usuario = Usuario.objects.get(nome=nome_ou_email)
            else:
                messages.error(request, 'Usuario invalido')
                return render_to_response('login.html', {}, context_instance=RequestContext(request))

            if senha == usuario.senha:
                request.session['email'] = usuario.email
                return redirect('/app')
            else:
                messages.error(request, 'Senha Incorreta')
            return redirect('/')
            # return render_to_response('login.html', {}, context_instance=RequestContext(request))
        except:
            messages.error(request, 'Usuario nao cadastrado')
            return redirect('/')
            # return render_to_response('login.html', {}, context_instance=RequestContext(request))



def app(request):
    usuario = Usuario.objects.get(email=request.session['email'])
    compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
    return render_to_response('app.html', {'usuario': usuario, 'usuarios': Usuario.objects.all(),
                                           'compartilhados': compartilhados}, context_instance=RequestContext(request))


def view_pasta(request, id):
    usuario = Usuario.objects.get(email=request.session['email'])
    compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
    pasta = Pasta.objects.get(id=id)
    return render_to_response('view_pasta.html', {'usuario': usuario, 'pasta': pasta, 'usuarios': Usuario.objects.all(),
                                                  'compartilhados': compartilhados},
                              context_instance=RequestContext(request))


def view_file(request, id):
    usuario = Usuario.objects.get(email=request.session['email'])
    arquivo = Arquivo.objects.get(id=id)
    if request.method == 'GET':
        file = arquivo.arquivo
        file.open(mode='rb')
        content = file.readlines()
        file.close()
        return render_to_response('view_file.html', {'usuario': usuario, 'arquivo': arquivo, 'content': content,
                                                     'usuarios': Usuario.objects.all()},
                                  context_instance=RequestContext(request))


def create_arquivo(request):
    usuario = Usuario.objects.get(email=request.session['email'])
    compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
    if request.method == 'GET':
        return render_to_response('create_file.html', {'usuario': usuario,
                                                       'usuarios': Usuario.objects.all(),
                                                       'compartilhados': compartilhados},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        nome = request.POST['nome']
        tipo = request.POST['tipo']
        if 'pasta' in request.POST:
            pasta = Pasta.objects.get(id=request.POST['pasta'])
        else:
            pasta = None
        try:
            arquivo_temp = Arquivo.objects.get(nome=nome)
            messages.error(request, 'Ja existe arquivo com este nome')
            return render_to_response('create_file.html', {'usuario': usuario,
                                                           'usuarios': Usuario.objects.all(),
                                                           'compartilhados': compartilhados},
                                      context_instance=RequestContext(request))
        except:
            try:
                file = ContentFile(request.POST['content'])
                arquivo = Arquivo(nome=nome, tipo=tipo, pasta=pasta)
                arquivo.arquivo.save(nome + '.' + tipo, file)
                arquivo.save()
                usuario.arquivos.add(arquivo)
                usuario.save()
                messages.success(request, 'Arquivo adicionado com sucesso')
                if pasta:
                    return redirect('/pasta/' + str(pasta.id))
                else:
                    return redirect('/')
            except:
                messages.error(request, 'Nao foi possivel criar novo arquivo')
                return render_to_response('create_file.html', {'usuario': usuario,
                                                           'usuarios': Usuario.objects.all(),
                                                           'compartilhados': compartilhados},
                                      context_instance=RequestContext(request))


def edit_arquivo(request, id):
    usuario = Usuario.objects.get(email=request.session['email'])
    arquivo = Arquivo.objects.get(id=id)
    if request.method == 'GET':
        file = arquivo.arquivo
        file.open(mode='rb')
        content = file.readlines()
        file.close()
        return render_to_response('edit_file.html', {'usuario': usuario, 'arquivo': arquivo, 'content': content,
                                                     'usuarios': Usuario.objects.all()},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        myfile = ContentFile(request.POST['content'])
        nome_arquivo = request.POST['nome']
        tipo_arquivo = request.POST['tipo']

        try:
            arq_temp = Arquivo.objects.get(nome=nome_arquivo)
            messages.error(request, 'Ja existe arquivo com este nome')
            return redirect('/app')
        except:
            arquivo.arquivo.save(str(nome_arquivo) + '.' + tipo_arquivo, myfile)
            arquivo.nome = nome_arquivo
            arquivo.tipo = tipo_arquivo
            arquivo.save()
            myfile.open(mode='rb')
            content = myfile.readlines()
            myfile.close()
            messages.success(request, 'Alterado com sucesso')
            return render_to_response('edit_file.html', {'arquivo': arquivo, 'content': content,
                                                     'usuarios': Usuario.objects.all()},
                                  context_instance=RequestContext(request))


def edit_pasta(request, id):
    usuario = Usuario.objects.get(email=request.session['email'])
    pasta = Pasta.objects.get(id=id)
    if request.method == 'GET':
        return render_to_response('edit_pasta.html', {'usuario': usuario, 'pasta': pasta},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        titulo_pasta = request.POST['titulo']
        try:
            pasta_temp = Pasta.objects.get(titulo=titulo_pasta)
            messages.error(request, 'Ja existe pasta com esse nome')
            return redirect('/app')
        except:
            pasta.titulo = titulo_pasta
            pasta.save()
            messages.success(request, 'Alterado com sucesso')
            return redirect('/app')


def compartilhar_amigo(request, id):
    arquivo = Arquivo.objects.get(id=id)
    id_usuario = request.POST['id_usuario']
    usuario = Usuario.objects.get(id=id_usuario)
    if request.POST['habilitado'] == '1':
        habilitado = True
    else:
        habilitado = False
    comp = Compartilhado(usuario=usuario, arquivo=arquivo, habilitado=habilitado)
    comp.save()
    messages.success(request, 'Compartilhado com sucesso')
    return redirect('/app')


def notificacoes(request):
    usuario = Usuario.objects.get(email=request.session['email'])
    compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
    for comp in compartilhados:
        comp.status = True
        comp.save()
    return render_to_response('notificacoes.html', {'usuario': usuario,
                                                    'usuarios': Usuario.objects.all(),
                                                    'compartilhados': compartilhados,
                                                    'compartilhados_cmg': Compartilhado.objects.filter(usuario=usuario)},
                              context_instance=RequestContext(request))


def nova_pasta(request):
    if request.method == 'GET':
        usuario = Usuario.objects.get(email=request.session['email'])
        compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
        return render_to_response('nova_pasta.html', {'usuario': usuario,
                                                      'usuarios': Usuario.objects.all(),
                                                      'compartilhados': compartilhados},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        titulo = request.POST['titulo']
        descricao = request.POST['descricao']
        if 'pasta' in request.POST:
            past = Pasta.objects.get(id=request.POST['pasta'])
        else:
            past = None
        try:
            pasta_temp = Pasta.objects.get(titulo=titulo)
            messages.error(request, 'Ja existe pasta com esse nome')
            return render_to_response('nova_pasta.html', {}, context_instance=RequestContext(request))
        except:
            try:
                pasta = Pasta(titulo=titulo, desc=descricao)
                pasta.save()
                usuario = Usuario.objects.get(email=request.session['email'])
                usuario.pastas.add(pasta)
                usuario.save()
                messages.success(request, 'Pasta criada com sucesso')
                return redirect('/app')
            except:
                messages.error(request, 'Nao foi possivel criar a pasta')
                return render_to_response('nova_pasta.html', {}, context_instance=RequestContext(request))


def remove_pasta(request, id):
    try:
        pasta = Pasta.objects.get(id=id)
        pasta.status = False
        pasta.save()
        for arq in pasta.arquivo_set.all():
            arq.status = False
            arq.save()
        messages.success(request, 'Pasta removida com sucesso')
    except:
        messages.error(request, 'Nao foi possivel remover a pasta')
    return redirect('/app')


def lixeira(request):
    usuario = Usuario.objects.get(email=request.session['email'])
    compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
    return render_to_response('lixeira.html', {'usuario': usuario,
                                               'usuarios': Usuario.objects.all(),
                                               'compartilhados': compartilhados},
                              context_instance=RequestContext(request))


def remove_arquivo(request, id):
    try:
        usuario = Usuario.objects.get(email=request.session['email'])
        arquivo = Arquivo.objects.get(id=id)
        pasta = arquivo.pasta
        arquivo.status = False
        arquivo.save()
        messages.success(request, 'Arquivo removido com sucesso')
        if pasta:
            return redirect('/pasta/' + str(pasta.id))
        else:
            return redirect('/')
    except:
        messages.error(request, 'Nao foi possivel remover o arquivo')
        return redirect('/')


def upload_arquivo(request):
    usuario = Usuario.objects.get(email=request.session['email'])
    compartilhados = Compartilhado.objects.filter(usuario=usuario, status=False)
    if request.method == 'GET':
        return render_to_response('upload.html', {'usuario': usuario,
                                                  'usuarios': Usuario.objects.all(),
                                                  'compartilhados':compartilhados}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        try:
            nome = request.POST['nome']
            arquivo = request.FILES['file']
            tipo = request.POST['tipo']
            if 'pasta' in request.POST:
                pasta = Pasta.objects.get(id=request.POST['pasta'])
            else:
                pasta = None
            arquivo = Arquivo(nome=nome, tipo=tipo, arquivo=arquivo, pasta=pasta)
            arquivo.save()
            usuario.arquivos.add(arquivo)
            usuario.save()
            messages.success(request, 'Arquivo adicionado com sucesso')
            if pasta:
                return redirect('/pasta/' + str(pasta.id))
            else:
                return redirect('/')
        except:
            messages.error(request, 'Nao foi possivel adicionar arquivo')
            return redirect('/')


def logout(request):
    request.session.clear()
    return redirect('/')
