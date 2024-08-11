from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib.messages import add_message
from .models import Empresas, Documento, Metricas
from investidores.models import PropostaInvestimento

def cadastrar_empresa(request):
    print(request.user.is_authenticated)
    print(request.user)
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')    
    if request.method == "GET":
        return render(request, 'cadastrar_empresa.html', {'tempo_existencia': Empresas.tempo_existencia_choices, 'areas': Empresas.area_choices })
    elif request.method == "POST":
        try:
            empresa = Empresas(
                user = request.user,
                nome = request.POST.get('nome'),
                cnpj = request.POST.get('cnpj'),
                site = request.POST.get('site'),
                tempo_existencia = request.POST.get('tempo_existencia'),
                descricao = request.POST.get('descricao'),
                data_final_captacao = request.POST.get('data_final'),
                percentual_equity = request.POST.get('percentual_equity'),
                estagio = request.POST.get('estagio'),
                area = request.POST.get('area'),
                publico_alvo = request.POST.get('publico_alvo'),
                valor = request.POST.get('valor'),
                pitch = request.FILES.get('pitch'),
                logo = request.FILES.get('logo')
            )
            empresa.save()
        except:
            add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/empresarios/cadastrar_empresa')        
    add_message(request, constants.SUCCESS, 'Empresa criada com sucesso')
    return redirect('/empresarios/cadastrar_empresa')

def listar_empresas(request):    
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')    
    if request.method == "GET":
        empresas = Empresas.objects.filter(user=request.user)        
        return render(request, 'listar_empresas.html', {'empresas': empresas})

def empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    if empresa.user != request.user:
        add_message(request, constants.ERROR, "Empresa não disponível para o usuário")
        return render(request, 'listar_empresas.html')    
    if request.method == "GET":
        documentos = Documento.objects.filter(empresa=empresa)
        proposta_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
        percentual_vendido = 0
        for pi in proposta_investimentos:
            if pi.status == 'PA':
                percentual_vendido = percentual_vendido + pi.percentual
        
        total_captado = sum(proposta_investimentos.filter(status='PA').values_list('valor', flat=True))
        valuation_atual = (100 * float(total_captado)) / float(percentual_vendido) if percentual_vendido != 0 else 0
        proposta_investimentos_enviada = proposta_investimentos.filter(status='PE')
        return render(request, 'empresa.html', {'empresa': empresa, 'documentos': documentos, 
                            'proposta_investimentos_enviada': proposta_investimentos_enviada, 
                            'percentual_vendido': int(percentual_vendido), 
                            'total_captado': total_captado, 
                            'valuation_atual': valuation_atual})
        
    
def add_doc(request, id):
    empresa = Empresas.objects.get(id=id)
    if empresa.user != request.user:
        add_message(request, constants.ERROR, "Empresa não disponível para o usuário")
        return render(request, 'listar_empresas.html')
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    extensao = arquivo.name.split('.')

    if extensao[1] != 'pdf':
        add_message(request, constants.ERROR, "Envie apenas PDF's")
        return redirect(f'/empresarios/empresa/{empresa.id}')
    
    if not arquivo:
        add_message(request, constants.ERROR, "Envie um arquivo")
        return redirect(f'/empresarios/empresa/{empresa.id}')
        
    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo
    )
    documento.save()
    add_message(request, constants.SUCCESS, "Arquivo cadastrado com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')

def excluir_dc(request, id):
    documento = Documento.objects.get(id=id)
    if documento.empresa.user != request.user:
        add_message(request, constants.ERROR, "Esse documento não é seu")
        return redirect(f'/empresarios/empresa/{documento.empresa.id}')
    
    documento.delete()
    add_message(request, constants.SUCCESS, "Documento excluído com sucesso")
    return redirect(f'/empresarios/empresa/{documento.empresa.id}')

def add_metrica(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    valor = request.POST.get('valor')
    
    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor
    )
    metrica.save()

    add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')

def gerenciar_proposta(request, id):
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)

    if acao == 'aceitar':
        add_message(request, constants.SUCCESS, 'Proposta aceita')
        pi.status = 'PA'
    elif acao == 'recusar':
        add_message(request, constants.SUCCESS, 'Proposta recusada')
        pi.status = 'PR'

    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')
