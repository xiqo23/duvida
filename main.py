import cv2
import touch as touch
from kivy.uix.scatterlayout import ScatterLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy_garden.mapview import MapView, MapMarker
from kivy.core.window import Window
from kivy.graphics.transformation import Matrix
from kivy.uix.scatter import Scatter
import psycopg2
from os.path import exists

class GerenciadorTelas (ScreenManager):
    """def __init__(self,**kwargs):
        super().__init__(**kwargs)
        print("funcionou")"""

    pass

class Tela1 (Screen):
    pass

class Tela2 (Screen):

    #Plotar um marcador no mapa atual
    def plotarmap(self, *args):

        a = self.ids.vt.text  # Toponimo que o usuário selecionou
        # conexão com o banco
        host = 'localhost'
        dbname = 'Maps_antigos'
        user = 'postgres'
        password = 'qwert'
        conn_string = 'host={0} user={1} dbname={2} password={3}'.format(host, user, dbname, password)
        conect = psycopg2.connect(conn_string)

        # consulta ao banco para pegar o pixel x e y do toponimo escolhido pelo usuário
        cursor = conect.cursor()
        cursor.execute(f"""
                       SELECT shape_localizacao."LATITUDE", shape_localizacao."LONGITUDE"
                       FROM shape_localizacao
                       INNER JOIN tabela_toponimos
                       ON tabela_toponimos."identificador" = shape_localizacao."N_ID"
                       WHERE tabela_toponimos.top_antigo = '{a}' order   by "TOP_ATUAL"  asc;
                   """)
        b = cursor.fetchall()  # Resultado da consulta vem em uma Lista/tupla

        Latitude = (b[0][0])  # valor do x extraido da Lista
        Longitude = (b[0][1])  # valor do extraido da Lista
        self.ids.marcador.lat=Latitude
        self.ids.marcador.lon=Longitude
        self.ids.mapa_principal.center_on(Latitude,Longitude)
        return

    #Plotar na imagem um criculo
    def plotarimagem (self, *args):

        a = self.ids.em.disabled #EM
        b = self.ids.vm.disabled #ET
        c = self.ids.vt.text #Toponimo que o usuário selecionou

        #conexão com o banco
        host = 'localhost'
        dbname = 'Maps_antigos'
        user = 'postgres'
        password = 'qwert'
        conn_string = 'host={0} user={1} dbname={2} password={3}'.format(host, user, dbname, password)
        conect = psycopg2.connect(conn_string)

        #consulta ao banco para pegar o pixel x e y do toponimo escolhido pelo usuário
        cursor = conect.cursor()
        cursor.execute(f"""
                SELECT tabela_toponimos.pixel_pos_x,tabela_toponimos.pixel_pos_y
                FROM shape_localizacao
                INNER JOIN tabela_toponimos
                ON tabela_toponimos."identificador" = shape_localizacao."N_ID"
                WHERE tabela_toponimos.top_antigo = '{c}' order   by "TOP_ATUAL"  asc;
            """)
        d = cursor.fetchall() #Resultado da consulta vem em uma Lista/tupla
        x = int(d[0][0])    #valor do x extraido da Lista
        y = int(d[0][1])    # valor do extraido da Lista

    #Se a pessoa quiser escolher um mapa espacifico (EM = Escolher mapa)
        if a == False:
            map = "IMG_MAPAS/"+self.ids.em.text+".jpg"
            image = cv2.imread(map)
            cv2.circle(image, (x,y), 100, (0, 0, 255), 8)
            cv2.imwrite("teste2.jpg", image)
            cv2.waitKey(0)
            self.ids.img.source="teste2.jpg"

    # Se a pessoa quiser escolher um toponimo (ET = Escolher toponimo)
        if b == False:
            map = "IMG_MAPAS/"+self.ids.vm.text+".jpg"
            image = cv2.imread(map)
            cv2.circle(image, (x,y), 100, (0, 0, 255), 8)
            cv2.imwrite("teste2.jpg", image)
            cv2.waitKey(0)
            self.ids.img.source="teste2.jpg"
        self.ids.reset.disabled = False

    #Fazer uma descrição dos resultados que aprecem na tela
    def descricaoresultado(self):
        c = self.ids.vt.text  # Toponimo que o usuário selecionou

        #conexão com o banco
        host = 'localhost'
        dbname = 'Maps_antigos'
        user = 'postgres'
        password = 'qwert'
        conn_string = 'host={0} user={1} dbname={2} password={3}'.format(host, user, dbname, password)
        conect = psycopg2.connect(conn_string)

        #consulta ao banco para pegar o pixel x e y do toponimo escolhido pelo usuário
        cursor = conect.cursor()
        cursor.execute(f"""
                SELECT shape_localizacao."TOP_ATUAL",tabela_toponimos.top_antigo, tabela_toponimos.pixel_pos_x,tabela_toponimos.pixel_pos_y,
                shape_localizacao."LATITUDE",shape_localizacao."LONGITUDE", tabela_toponimos.map_ref, tabela_toponimos.ano
                FROM shape_localizacao
                INNER JOIN tabela_toponimos
                ON tabela_toponimos."identificador" = shape_localizacao."N_ID"
                WHERE tabela_toponimos.top_antigo = '{c}' order   by "TOP_ATUAL"  asc;

            """)
        a = cursor.fetchall() #Resultado da consulta vem em uma Lista/tupla
        Toponimo_atual = a[0][0]
        Toponimo_antigo = a[0][1]
        Imagem_pox_x = int(a[0][2])
        Imagem_pox_y = int(a[0][3])
        Latitude = a[0][4]
        Longitude = a[0][5]
        Nome_mapa_antigo = (a[0][6]).upper()
        Ano_mapa = a[0][7]
        b=(f"""
        MAPA: {Nome_mapa_antigo}     ANO:{Ano_mapa}
        Nome atual: {Toponimo_atual}      Latitude: {Latitude}        Longitude: {Longitude}
        Nome antigo: {Toponimo_antigo}         Posição na img Y: {Imagem_pox_y}px       Posição na img X: {Imagem_pox_x}px
        """)
        self.ids.descricao.text=b

    #Para resetar a visão do mapa, bloqueando tudo novamente
    def resetar(self):

        #setar a imagem para o logo do geocart
        self.ids.img.source = "IMG_INTERFACE/GEOCART_INICIAL.jpg"
        trans = Matrix().scale(1, 1, 1) # x , y, z
        self.ids['scarter_img'].transform = trans

        #Demarca os check box
        self.ids.check1.active=False
        self.ids.check2.active=False

        #Desabilita as listas suspensas
        self.ids.em.disabled =True
        self.ids.vt.disabled=True
        self.ids.et.disabled=True
        self.ids.vm.disabled=True

        #Desabilita os botões de plotar e de resetar
        self.ids.reset.disabled = True
        self.ids.plotar.disabled = True

        #Centralizar o mapa novamente no rio de janeiro e mover o marcador para lat 0 long 0
        self.ids.mapa_principal.center_on(-22.9423, -42.03376)
        self.ids.mapa_principal.zoom=7
        self.ids.marcador.lat=0
        self.ids.marcador.lon=0

        #Ajustar o texto da lista suspensa para
        self.ids.em.text = "Escolha o mapa"
        self.ids.vt.text="Verifique os toponimos do mapa"
        self.ids.et.text= "Escolha o toponimo"
        self.ids.vm.text = "Verifique os mapas que ele aparece"

        self.ids.descricao.text=''

    #Se eu marcar a chekbox 1 ele vai habilitar os botões para eu escolher o mapa (em)
    def checkbox1(self):

        #Pegar todos os mapas que estão no banco e listar, adicionado na lista do spiner
        host = 'localhost'
        dbname = 'Maps_antigos'
        user = 'postgres'
        password = 'qwert'
        conn_string = 'host={0} user={1} dbname={2} password={3}'.format(host, user, dbname, password)
        conect = psycopg2.connect(conn_string)
        cursor = conect.cursor()
        cursor.execute('SELECT DISTINCT tabela_toponimos."map_ref" FROM tabela_toponimos order by "map_ref" asc;')
        a = cursor.fetchall()
        lista = []
        for x in range(len(a)):
            lista.append(a[x][0])
        self.ids.em.values = lista

        if self.ids.check1.active == True:
            self.ids.em.disabled=False
            self.ids.check2.active=False
            self.ids.et.disabled=True
            self.ids.vm.disabled = True
            self.ids.et.text = "Escolha o toponimo"
            self.ids.vm.text = "Verifique os mapas que ele aparece"
            self.ids.plotar.disabled = True

        if self.ids.check1.active == False:
            self.ids.em.disabled = True
            self.ids.vt.disabled = True
            self.ids.em.text = "Escolha o mapa"
            self.ids.vt.text = "Verifique os toponimos do mapa"
            self.ids.plotar.disabled = True

    #Depois de escolher o mapa (em), o botão de ver toponimos (vt)  é liberado
    def liberarVT(self):
        a = self.ids.em.text
        #Pegar todos os toponimos que estão no banco, referente ao mapa selecionado na lista do spiner
        host = 'localhost'
        dbname = 'Maps_antigos'
        user = 'postgres'
        password = 'qwert'
        conn_string = 'host={0} user={1} dbname={2} password={3}'.format(host, user, dbname, password)
        conect = psycopg2.connect(conn_string)
        cursor = conect.cursor()
        cursor.execute(f'''
            SELECT shape_localizacao."TOP_ATUAL"
            FROM shape_localizacao            
            INNER JOIN tabela_toponimos            
            ON tabela_toponimos."identificador" = shape_localizacao."N_ID"            
            WHERE tabela_toponimos.map_ref = '{a}' order   by "TOP_ATUAL"  asc;''')
        b = cursor.fetchall()
        lista = []
        for x in range(len(b)):
            lista.append(b[x][0])
        self.ids.vt.values = lista

        b = self.ids.em.text
        if b != "Escolha o mapa":
            self.ids.vt.disabled = False
        if b == "Escolha o toponimo":
            self.ids.vt.disabled = True

    #Se eu marcar a chekbox 2 ele vai habilitar os botões para eu escolher o toponimo (et)
    def checkbox2 (self):
        if self.ids.check2.active == True:
            self.ids.et.disabled=False
            self.ids.check1.active=False
            self.ids.em.disabled=True
            self.ids.em.text = "Escolha o mapa"
            self.ids.vt.disabled = True
            self.ids.vt.text = "Verifique os toponimos do mapa"
            self.ids.plotar.disabled = True
        if self.ids.check2.active == False:
            self.ids.et.disabled = True
            self.ids.et.text = "Escolha o toponimo"
            self.ids.vm.disabled = True
            self.ids.vm.text = "Verifique os mapas que ele aparece"

    # Depois de escolher o toponimo (et), o botão de ver mapa (vm)  é liberado
    def liberarVM(self):
        a = self.ids.et.text
        if a != "Escolha o toponimo":
            self.ids.vm.disabled = False
        if a == "Escolha o toponimo":
            self.ids.vm.disabled = True

    #Liberar o botão de plotar apenas quando todas as opções tiverem sido completas
    def liberarplotar(self):
        a = self.ids.vm.text
        b = self.ids.vt.text
        if a != "Verifique os mapas que ele aparece":
            self.ids.plotar.disabled = False
        if b !="Verifique os toponimos do mapa":
            self.ids.plotar.disabled = False

# Classe vai construir a aplicação
class TesteApp (MDApp):
    def build (self):
        self.theme_cls.theme_style = "Dark"
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (1000, 700)
        Window.pos = (0,0)
        return
TesteApp().run()