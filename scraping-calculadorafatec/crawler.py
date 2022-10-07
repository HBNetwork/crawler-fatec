import datetime
import pprint
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from tqdm import tqdm

def salvandoDadosVestibularDFtoCSV(df_,nome_arq,path='ds'):
    df_.to_csv(f'{path}/{nome_arq}.csv', sep=';',index=False)

# precisa deixar global
def urlListaClassificacaoVestibular(url):
    driver = webdriver.Chrome()
    return driver.get(url)

def popularSelect(driver,id_Xpath):
    return  Select(driver.find_element_by_id(f'{id_Xpath}'))

def criarDicionario(select_,fields):
    lista_ = [] 
    for c in range(len (select_.options)):
        if 'Selecione...' not in select_.options[c].text:
            #key_ = int(select_.options[c].get_attribute("value"))
            key_= (int(select_.options[c].get_attribute("value")) if select_.options[c].get_attribute("value").isdigit() == True  else c)
            value_= select_.options[c].text
            lista_.append({fields[0]:key_,fields[1]:value_})
    return lista_

def criarDataFrame(l):
     return pd.DataFrame(l)

def fatecs():
    # não precisa disso agora.
    selectFatecs = Select(classificacao_geral_vest_fatec.find_element(By.ID, 'CodFatec'))
    listaFatecs = criarDicionario(selectFatecs,['id','fatec'])

    with open('ds/listafatecs.txt','a', encoding="utf-8") as arquivo:
        arquivo.write(str(listaFatecs))

    dfFatec = criarDataFrame(listaFatecs)
    salvandoDadosVestibularDFtoCSV(dfFatec,"listaFatecs")
    
    return dfFatec


def cursos():
    buscarCursosPopular('https://www.vestibularfatec.com.br/unidades-cursos/?q=')
    dfCursos = pd.read_csv('ds/listaCursos.csv',sep=';')
    return dfCursos


def buscarCursosPopular(url_cursos):
    rCurso = requests.get(url_cursos)
    soupCurso = bs(rCurso.content,'html.parser')    
    divCursos = soupCurso.find(id = "cursos")
    lista_links=divCursos.find_all("a")
    #lista_ = [{'id':245,'curso':'Gestão Empresarial - EaD'}]
    lista_=[]
    
    for c in range (len(lista_links)):
        key = int((divCursos.find_all('a')[c]['href']).split("=")[1])
        value= divCursos.find_all("a")[c].get_text()
        lista_.append({'id':key,'curso':value})
        
    return salvandoDadosVestibularDFtoCSV(criarDataFrame(lista_),'listaCursos')

def curso_periodo(txt):
    #recebe uma string, faz uma lógica para separar em duas partes. Devolvendo um array de 2 itens. O índice 0 é o curso e o outro o período.
    return (txt.replace(")", "")).split('(')

def demandas_ano_semestre():
    demanda_por_curso = webdriver.Chrome()
    demanda_por_curso.get("https://www.vestibularfatec.com.br/demanda/")

    select_ano_sem = Select(demanda_por_curso.find_element(By.NAME,'ano-sem'))
    lista_ano_sem = criarDicionario(select_ano_sem,['id','ano-sem'])

    with open('ds/lista_demanda_ano_semestre.txt','a', encoding="utf-8") as arquivo:
        arquivo.write(str(lista_ano_sem))

    dfDemandaAnoSemestre = criarDataFrame(lista_ano_sem)
    salvandoDadosVestibularDFtoCSV(dfDemandaAnoSemestre,"listaDemandaAnoSemestre")
   

def demanda_curso():
    demanda_por_curso = webdriver.Chrome()
    demanda_por_curso.get("https://www.vestibularfatec.com.br/demanda/")

    selectOptionsAnoSem = Select(demanda_por_curso.find_element(By.NAME,'ano-sem'))
    selectOptionsAnoSem.select_by_value('20222') #informar o ano e semestre que quer capturar.
    frmdemanda = demanda_por_curso.find_element(By.ID, "formDemanda")

    frmdemanda.find_element(By.CSS_SELECTOR,'button.btn'). submit()

    selectFatecsDemanda = Select(demanda_por_curso.find_element(By.ID,'FATEC'))
    listaFatecsDemanda = criarDicionario(selectFatecsDemanda,['id','fatec'])
    dfFatecDemanda = criarDataFrame(listaFatecsDemanda)
    print(dfFatecDemanda.head())
    armazenando_resultado_demanda=[]
 
    for i in tqdm(range(len (dfFatecDemanda.head(5)))):
        parcial_demanda = {}
        id_ = dfFatecDemanda.loc[i,'id']
        fatec_ = dfFatecDemanda.loc[i,'fatec']
        selectFatecs = Select(demanda_por_curso.find_element(By.ID,'FATEC'))
        selectFatecs.select_by_visible_text(fatec_)
        print(f'{fatec_} - {i+1}')

        demanda_por_curso.find_element(By.CSS_SELECTOR, 'button.btn').submit()  
        
        tabela_demanda = demanda_por_curso.find_element(By.CSS_SELECTOR, 'table.table')
        results=[]
        for count,cell in enumerate(tabela_demanda.find_elements(By.CSS_SELECTOR,'tbody td')):
            results.append(cell.text)
            #print(cell.text,count)    
        time.sleep(1)
        print(results)
        #x = {'fatec':fatec_,'demanda'result:results}
        demanda_por_curso.back()

'''
lista_info_vestibular_fatec = {
    'cod_curso':'' ,
    'nome_curso':'',
    'cod_instituicao':'',
    'instituicao':'',
    'ano':'', 
    'semestre':'',
    'periodo':'',
    'qtde_vagas':'',
    'qtde_inscrito':'',
    'demanda':'',
    'nota_corte':'',
    'nota_maxima':''
}
----------------------------------------------------
    cod_curso-> Sitema da Calculadora
    cod_instituicao -> Sistema da Calculadora
    ano -> ano do vestibular
    semeste-> semestre do vestibular
    periodo -> da busca (UPPER())
    ROBO DEMANDA
    qtde_vagas-> preencher através de outro robo
    qtde_inscrito->
    demanda-> realizar o cálculo
    nota_corte -> nota min
    nota_maxima -> nota max
'''

def resultado_fatec():
    resultado_tabela = webdriver.Chrome()
    resultado_tabela.get("https://www.vestibularfatec.com.br/classificacao/lista.asp?codfatec=1&codescolacurso=1999&o=1")

    #tabela_ = resultado_tabela.find_elements_by_css_selector('.table.table-bordered.table-striped')
    #tabela_ = resultado_tabela.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div[2]/table')

    #tabela_ = resultado_tabela.find_elements_by_class_name('table')

    tabela_ =resultado_tabela.find_element_by_css_selector('table.table')

    #-Processo para verificar a posição da NOTA e SITUAÇÃO
    pos_nota = 0
    pos_situacao = 0
        
    for count,cell in enumerate(tabela_.find_elements_by_css_selector('thead th')):
        print(cell.text,count)
        if (cell.text =='Situação'):
            pos_situacao = count
        if (cell.text =='Nota'):
            pos_nota = count

def semestre(mes):
    semestre = 2
    if mes <=6:
        semestre=1
    return semestre
def ajustarNota(detalhe_nota,pos=-4):
    #test = '71.00079-6 ANA  77,970 Sim Sim CLASSIFICADO'
    #print(detalhe_nota.text.upper().split(' '))
    return detalhe_nota.text.upper().split(' ')[pos]

if __name__ == "__main__":
    #classificacao_geral_vest_fatec = urlListaClassificacaoVestibular('https://www.vestibularfatec.com.br/classificacao/fatec.asp')
    classificacao_geral_vest_fatec = webdriver.Chrome()
    classificacao_geral_vest_fatec.get("https://www.vestibularfatec.com.br/classificacao/fatec.asp")
    dfFatec = fatecs()
   
    dfCursos = cursos()    

    resultado_vestibular_da_fatec = []
    resultado_vestibular_da_fatec2 = [] #Organiza cada fatec em uma array.
    #demanda_curso()
    # Criando um dataframe do pandas
    
    #df = dfFatec.copy(deep=True)
    #print(df)

def procurar_id_curso_por_nome(df, curso):
    #PRECISA AJUSTAR ESSE PONTO.
    x = df.loc[df['curso'] == curso]
    print(x.id)
    return x.id

for i in tqdm(range(len (dfFatec.head(1)))):
    resultado_por_fatec=[]
    id_ = dfFatec.loc[i,'id']
    fatec_ = dfFatec.loc[i,'fatec']
    #CARREGA UMA LISTA COM OS DADOS DO SELECT DA PAGINA. RECEBE OS DADOS DA FATEC
    selectFatecs = Select(classificacao_geral_vest_fatec.find_element(By.ID,'CodFatec'))
    #NAVEGA NA FATEC DA VEZ. ELE FAZ ESSE CICLO, SEGUINDO O DATAFRAME. PREENCHIDO EM OUTRO MOMENTO OU PELA FUNÇÃO OU PELO CSV
    selectFatecs.select_by_visible_text(fatec_)
    #APÓS SELECIONAR NO COMBO A FATEC - CLICA NO BOTÃO PARA IR PARA A PÁGINA DA ESCOLHA DO CURSO
    classificacao_geral_vest_fatec.find_element(By.XPATH,'//*[@id="formClassificacao"]/div[2]/button').click()
    #SEGURA A PÁGINA PARA QUE ELA POSSA ESTAR 100% CARREGADA PARA A PRÓXIMA ETAPA
    time.sleep(5)
    #PREENCHE A LISTA DE CURSOS OFERECIDAS NA FATEC SELECIONADA ANTERIRMENTE
    selectCursos = Select(classificacao_geral_vest_fatec.find_element(By.ID,'CodEscolaCurso'))
    #CRIA UM DICIONARIO PARA FACILITAR A NAVEGAÇÃO, ATRAVÉS DE UMA FUNÇÃO 
    listaDeCursos = criarDicionario(selectCursos,['id','curso'])
    #SEGURA A PÁGINA
    time.sleep(3)
    print(f'quantidade de cursos {len(selectCursos.options)}')
    time.sleep(1)
    #ENTRA EM UM LOOP PARA VISITAR TODOS OS CURSOS DA FATEC SELECIONADA
    for c in range(len (listaDeCursos)):
        lista_info_vestibular_fatec = {}
        #RECARREGA O OBJETO PARA NÃO PERDER O PONTEIRO. DÁ PARA MELHORAR ESSE TRECHO
        selectCursos = Select(classificacao_geral_vest_fatec.find_element(By.ID,'CodEscolaCurso'))
        print(f'{fatec_} - {listaDeCursos[c]["curso"]}')
        #ESSE VERIFICADOR IMPEDE QUE A OPÇÃO SELECIONE SEJA ITERADA
        if 'Selecione...' not in listaDeCursos[c]['curso']:
            #selectCursos.select_by_visible_text(listaDeCursos[c]['curso'])
            #RECUPERO O ID DO CURSO E PASSO PARA A FUNÇÃO DO SELENIUM PARA SELECIONAR O ITEM NO SELECT
            idC = str(listaDeCursos[c]['id'])
            selectCursos.select_by_value(idC)
            #REALIZO O CLICK PARA CHEGAR NA PRÓXIMA PÁGINA
            classificacao_geral_vest_fatec.find_element(By.XPATH,'//*[@id="formClassificacao"]/div[2]/button').click()   
            #SEGURO UM POUCO A PÁGINA PARA QUE CONSIGA CARREGAR. VERIFICAR SE EXISTE METÓDO MELHOR PARA AGUARDAR
            time.sleep(3)   
            #PEGO A URL ATUAL E CONCATENO COM AS INFORMAÇÕES DE IDENTIFICAÇÃO DA FATEC E CURSO.
            #ESSE TRECHO PRECISA SER ADAPTADO PARA CASO O USUÁRIO JÁ SEJA REDIRECIONADO PARA A PAGINA DESTINO. ISSO ACONTECE CASO NÃO TENHA LISTA DE CONVOCAÇÃO DE 2 CHAMADA
            url_lista_1chamada = classificacao_geral_vest_fatec.current_url
            #cod_curso = int(selectCursos.options[c].get_attribute("value"))
            url_lista_1chamada = (f'{url_lista_1chamada}?codfatec={id_}&codescolacurso={idC}&o=1')
            #REALIZO O CLICK PARA CONSULTAR A TABELA DE CLASSIFICAÇÃO COM AS NOTAS
            classificacao_geral_vest_fatec.find_element(By.XPATH,'/html/body/div[2]/div/div[2]/div/ul/li[1]/a').click()   
            time.sleep(3)
            #SELECIONO A TABELA COM O RESULTADO            
            tabela_ =classificacao_geral_vest_fatec.find_element(By.CSS_SELECTOR,'table.table')
            #AQUI ESTÁ UMA SACADA. COMO TEM CURSOS COM MUITOS INSCRITOS E AS VAGAS NO MÁXIMO SÃO DE 80 VAGAS. FAÇO UMA SELEÇÃO APENAS DOS 80 PRIMEIROS
            resultado80 = tabela_.find_elements(By.CSS_SELECTOR,'tbody tr:nth-child(-n + 100)')
            #print(resultado80)
            #SEGURO A PÁGINA PARA QUE POSSA CARREGAR
            time.sleep(5)
            #A NOTA MÁXIMA SEMPRE SERÁ O PRIMEIRO REGISTRO. POR ISSO ATRIBUIÇÃO DIRETA.
            nota_max= ajustarNota(resultado80[0])
            #print(ajustarNota(resultado80[32]))
            #AGORA PRECISO DESCOBRIR A NOTA MINÍMA(CORTE) OU SEJA O ÚLTIMO CONVOCADO
            nota_min = 0
            #FACO UMA ITERAÇÃO DENTRO DA LISTA COM OS 80 PRIMEIROS. PODERIAM AJUSTAR PARA PERCORRER DE FORMA MULTIPLO DE 5. POIS O MÍNIMO DE VAGAS É 30
            for i, linha in enumerate(resultado80):
                #print(f'#{i+1} - {linha.text}')
#               lista_info_vestibular_fatec = {}
                #DENTRO DESSA ITERAÇÃO, TENHO CERTEZA QUE PEGAREI APENAS O CONVOCADO COM OO IF, SEMPRE ATUALIZANDO A NOTA MIN A CADA PASSAGEM. ITERROMPO, QUANDO A CONDIÇÃO DO IF FOR FALSE
                if ('CLASSIFICADO' in linha.text.upper()): #or 'CONVOCADO'
                    nota_min = ajustarNota(linha)
                else:
                    break            
            print(f'NOTA MÁXIMA = {nota_max} | NOTA DE CORTE = {nota_min}')
            #NESTA ETAPA JÁ POSSUO OS DADOS PARA CRIAR UM OBJETO COMOS RESULTADOS DESTE CURSO, PERIODO E DESTA FATEC
            lista_info_vestibular_fatec['codcurso'] = procurar_id_curso_por_nome(dfCursos, curso_periodo(listaDeCursos[c]["curso"])[0]) #idC # Não é o código do Curso. Precisa fazer
            lista_info_vestibular_fatec['nome_curso'] = curso_periodo(listaDeCursos[c]["curso"])[0]#curso
            lista_info_vestibular_fatec['codfatec'] = id_
            lista_info_vestibular_fatec['instituicao'] = fatec_.strip()
            lista_info_vestibular_fatec['ano']= datetime.datetime.now().year
            lista_info_vestibular_fatec['semestre']= semestre(datetime.datetime.now().month)
            lista_info_vestibular_fatec['periodo'] = curso_periodo(listaDeCursos[c]["curso"])[1].upper()#periodo
            lista_info_vestibular_fatec['nota_corte'] = nota_min
            lista_info_vestibular_fatec['nota_maxima'] = nota_max
            #ARMAZENO O RESULTADO EM UMA LISTA. CRIO DUAS MANEIRAS DISTINTAS
            print(lista_info_vestibular_fatec)
            resultado_vestibular_da_fatec.append(lista_info_vestibular_fatec)            
            resultado_por_fatec.append(lista_info_vestibular_fatec)
            #RETORNO DUAS VEZES PARA RECOMEÇAR O PASSO A PASSO
            classificacao_geral_vest_fatec.back()
            classificacao_geral_vest_fatec.back()
            resultado_vestibular_da_fatec2.append(resultado_por_fatec)
    classificacao_geral_vest_fatec.back()
    time.sleep(1)


