import os
import threading
import webbrowser
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
import sys
from kivy.clock import mainthread

from services.api_client import enviar_mensagem_para_api

def resource_path(relative_path):
    """ Retorna o caminho absoluto do arquivo, compatível com PyInstaller """
    try:
        # PyInstaller cria a pasta temporária e coloca em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_path, 'assets', relative_path)


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Layout principal vertical
        layout_principal = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # Caminho absoluto da imagem dentro de frontend/assets/
        caminho_logo = resource_path('logo SOS1.png')

        # -----------------------------------------------------------------
        # 1. CABEÇALHO (Logo / Título)
        # -----------------------------------------------------------------
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=90, spacing=3)

        if os.path.exists(caminho_logo):
            logo = Image(
                source=caminho_logo,
                nocache=True,
                mipmap=True,
                size_hint=(1, None),
                height=80,
                allow_stretch=True,
                keep_ratio=True,
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            header.add_widget(logo)
        else:
            titulo_fallback = Label(
                text="[b]SOS Terminaram Comigo[/b]",
                markup=True,
                size_hint_y=None,
                height=35,
                font_size='18sp'
            )
            header.add_widget(titulo_fallback)


        layout_principal.add_widget(header)

        # -----------------------------------------------------------------
        # 2. BARRA DE BOTÕES (Profissional e Agendamento)
        # -----------------------------------------------------------------
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=38, spacing=6)

        btn_perfil = Button(
            text="👩‍⚕️ Psicóloga",
            background_normal='',
            background_color=(0.18, 0.50, 0.72, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size='12sp'
        )
        btn_perfil.bind(on_release=self.abrir_popup_perfil)

        btn_atendimento = Button(
            text="📅 Agendar",
            background_normal='',
            background_color=(0.20, 0.65, 0.35, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size='12sp'
        )
        btn_atendimento.bind(on_release=self.abrir_popup_atendimento)

        top_bar.add_widget(btn_perfil)
        top_bar.add_widget(btn_atendimento)
        layout_principal.add_widget(top_bar)

        # -----------------------------------------------------------------
        # 3. ÁREA DE CHAT (Histórico de Mensagens)
        # -----------------------------------------------------------------
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.chat_history = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=[5, 5, 5, 5]
        )
        self.chat_history.bind(minimum_height=self.chat_history.setter('height'))
        self.scroll.add_widget(self.chat_history)
        layout_principal.add_widget(self.scroll)

        # -----------------------------------------------------------------
        # 4. ÁREA INFERIOR (Input e Botão Enviar)
        # -----------------------------------------------------------------
        area_input = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=6)

        self.txt_mensagem = TextInput(
            hint_text="Escreva..........",
            multiline=False,
            size_hint_x=0.76,
            padding=[10, 10, 10, 10]
        )
        self.txt_mensagem.bind(on_text_validate=self.iniciar_envio)
        area_input.add_widget(self.txt_mensagem)

        self.btn_enviar = Button(
            text="Enviar",
            size_hint_x=0.24,
            background_normal='',
            background_color=(0.2, 0.6, 0.86, 1),
            bold=True
        )
        self.btn_enviar.bind(on_release=self.iniciar_envio)
        area_input.add_widget(self.btn_enviar)

        layout_principal.add_widget(area_input)
        self.add_widget(layout_principal)

        # Mensagem inicial da IA
        self.adicionar_mensagem(
            "Bom dia! Para um melhor atendimento preciso que você me responda 4 perguntas. 1ª. Qual o seu nome?", autor="ia")

    # ---------------------------------------------------------------------
    # POPUPS E AGENDAMENTO
    # ---------------------------------------------------------------------
    def abrir_popup_perfil(self, instance):
        conteudo = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        lbl_info = Label(
            text="Menu da Profissional:",
            bold=True,
            size_hint_y=None,
            height=25,
            font_size='14sp'
        )
        conteudo.add_widget(lbl_info)

        btn_apresentacao = Button(
            text="👩‍⚕️ Apresentação Profissional",
            background_normal='',
            background_color=(0.18, 0.50, 0.72, 1),
            size_hint_y=None,
            height=42,
            font_size='13sp'
        )
        btn_apresentacao.bind(on_release=lambda x: self.abrir_popup_apresentacao(popup))
        conteudo.add_widget(btn_apresentacao)

        btn_redes = Button(
            text="📱 Redes Sociais",
            background_normal='',
            background_color=(0.8, 0.3, 0.5, 1),
            size_hint_y=None,
            height=42,
            font_size='13sp'
        )
        btn_redes.bind(on_release=lambda x: self.abrir_popup_redes_sociais(popup))
        conteudo.add_widget(btn_redes)

        btn_agendar = Button(
            text="📅 Agendar Atendimento",
            background_normal='',
            background_color=(0.20, 0.65, 0.35, 1),
            size_hint_y=None,
            height=42,
            font_size='13sp'
        )
        btn_agendar.bind(on_release=lambda x: self.chamar_agendamento(popup))
        conteudo.add_widget(btn_agendar)

        btn_fechar = Button(
            text="Fechar",
            size_hint_y=None,
            height=38,
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        conteudo.add_widget(btn_fechar)

        popup = Popup(
            title="Opções da Psicóloga",
            content=conteudo,
            size_hint=(0.9, 0.6)
        )
        btn_fechar.bind(on_release=popup.dismiss)
        popup.open()

    def chamar_agendamento(self, popup_anterior):
        popup_anterior.dismiss()
        self.abrir_popup_atendimento(None)

    def abrir_popup_redes_sociais(self, popup_anterior):
        popup_anterior.dismiss()
        conteudo = BoxLayout(orientation='vertical', spacing=10, padding=10)

        lbl = Label(
            text="Acompanhe nas redes:",
            bold=True,
            size_hint_y=None,
            height=25,
            font_size='14sp'
        )
        conteudo.add_widget(lbl)

        btn_insta = Button(
            text="Instagram",
            background_normal='',
            background_color=(0.7, 0.2, 0.5, 1),
            size_hint_y=None,
            height=42,
            font_size='13sp'
        )
        # Atualize o link se necessário
        btn_insta.bind(on_release=lambda x: webbrowser.open("https://instagram.com"))
        conteudo.add_widget(btn_insta)

        btn_fb = Button(
            text="Facebook",
            background_normal='',
            background_color=(0.2, 0.4, 0.7, 1),
            size_hint_y=None,
            height=42,
            font_size='13sp'
        )
        # Atualize o link se necessário
        btn_fb.bind(on_release=lambda x: webbrowser.open("https://facebook.com"))
        conteudo.add_widget(btn_fb)

        btn_fechar = Button(
            text="Voltar",
            size_hint_y=None,
            height=38,
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        conteudo.add_widget(btn_fechar)

        popup = Popup(
            title="Redes Sociais",
            content=conteudo,
            size_hint=(0.9, 0.5)
        )
        btn_fechar.bind(on_release=popup.dismiss)
        popup.open()

    def abrir_popup_apresentacao(self, popup_anterior):
        popup_anterior.dismiss()
        conteudo = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Foto da Psicóloga com alta nitidez e sem cache
        caminho_foto = resource_path('jessica4.png')
        if os.path.exists(caminho_foto):
            foto = Image(
                source=caminho_foto,
                nocache=True,
                mipmap=True,
                size_hint_y=None,
                height=100,
                allow_stretch=True,
                keep_ratio=True
            )
            if foto.texture:
                foto.texture.min_filter = 'linear'
                foto.texture.mag_filter = 'linear'
            conteudo.add_widget(foto)

        texto_apresentacao = (
            "[b]Dra. Jéssica Vella Dias \nPsicóloga Responsável[/b]\n"
            "[size=12sp]CRP: 00/00000[/size]\n\n"
            "Especialista em acolhimento emocional, luto por término de relacionamento, "
            "autoestima e regulação emocional.\n\n"
            "Atendimento humanizado presencial e online."
        )

        lbl = Label(
            text=texto_apresentacao,
            markup=True,
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            font_size='13sp'
        )
        lbl.bind(width=lambda s, w: setattr(s, 'text_size', (w - 20, None)))
        conteudo.add_widget(lbl)

        btn_fechar = Button(
            text="Fechar",
            size_hint_y=None,
            height=38,
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        conteudo.add_widget(btn_fechar)

        popup = Popup(
            title="Apresentação Profissional",
            content=conteudo,
            size_hint=(0.9, 0.78)
        )
        btn_fechar.bind(on_release=popup.dismiss)
        popup.open()

    def abrir_popup_atendimento(self, instance):
        conteudo = BoxLayout(orientation='vertical', spacing=8, padding=10)

        lbl_info = Label(
            text="Escolha a modalidade:",
            bold=True,
            size_hint_y=None,
            height=25,
            font_size='14sp'
        )
        conteudo.add_widget(lbl_info)

        btn_tele = Button(
            text="💻 Teleconsulta (WhatsApp)",
            background_normal='',
            background_color=(0.20, 0.65, 0.35, 1),
            size_hint_y=None,
            height=42,
            font_size='13sp'
        )
        btn_tele.bind(on_release=lambda x: self.abrir_whatsapp("Olá! Gostaria de agendar uma Teleconsulta."))
        conteudo.add_widget(btn_tele)

        btn_presencial = Button(
            text="🏢 Atendimento Presencial",
            background_normal='',
            background_color=(0.18, 0.50, 0.72, 1),
            size_hint_y=None,
            height=42,
            font_size='13sp'
        )
        btn_presencial.bind(on_release=lambda x: self.abrir_popup_endereco(popup))
        conteudo.add_widget(btn_presencial)

        btn_fechar = Button(
            text="Voltar ao Chat",
            size_hint_y=None,
            height=38,
            background_normal='',
            background_color=(0.5, 0.5, 0.5, 1)
        )
        conteudo.add_widget(btn_fechar)

        popup = Popup(
            title="Agendamento",
            content=conteudo,
            size_hint=(0.9, 0.5)
        )
        btn_fechar.bind(on_release=popup.dismiss)
        popup.open()

    def abrir_popup_endereco(self, popup_anterior):
        popup_anterior.dismiss()
        conteudo = BoxLayout(orientation='vertical', spacing=8, padding=10)

        texto_end = (
            "[b]Consultório Presencial[/b]\n\n"
            "📍 Av. Principal, nº 1000 - Sala 302\n"
            "Centro Comercial / Edifício Saúde\n\n"
            "⏰ Segunda a Sexta: 08h às 19h"
        )

        lbl = Label(
            text=texto_end,
            markup=True,
            halign='center',
            font_size='13sp'
        )
        lbl.bind(width=lambda s, w: setattr(s, 'text_size', (w - 20, None)))
        conteudo.add_widget(lbl)

        btn_wpp = Button(
            text="Agendar via WhatsApp",
            background_normal='',
            background_color=(0.20, 0.65, 0.35, 1),
            size_hint_y=None,
            height=42,
            font_size='13sp'
        )
        btn_wpp.bind(on_release=lambda x: self.abrir_whatsapp("Olá! Gostaria de agendar um atendimento Presencial."))
        conteudo.add_widget(btn_wpp)

        btn_fechar = Button(
            text="Fechar",
            size_hint_y=None,
            height=38,
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        conteudo.add_widget(btn_fechar)

        popup_end = Popup(
            title="Endereço",
            content=conteudo,
            size_hint=(0.9, 0.55)
        )
        btn_fechar.bind(on_release=popup_end.dismiss)
        popup_end.open()

    def abrir_whatsapp(self, mensagem):
        # Altere o número abaixo para o número real com DDI + DDD (ex: 5547999999999)
        numero = "5511999483641"
        url = f"https://api.whatsapp.com/send?phone={numero}&text={mensagem.replace(' ', '%20')}"
        webbrowser.open(url)

    # ---------------------------------------------------------------------
    # LÓGICA DO CHAT
    # ---------------------------------------------------------------------
    def iniciar_envio(self, instance):
        texto = self.txt_mensagem.text.strip()
        if not texto:
            return

        self.adicionar_mensagem(texto, autor="usuario")
        self.txt_mensagem.text = ""
        self.btn_enviar.disabled = True

        threading.Thread(target=self._requisicao_ia_thread, args=(texto,), daemon=True).start()

    def _requisicao_ia_thread(self, texto):
        resposta = enviar_mensagem_para_api(texto)
        self.receber_resposta_ia(resposta)

    @mainthread
    def receber_resposta_ia(self, resposta):
        self.adicionar_mensagem(resposta, autor="ia")
        self.btn_enviar.disabled = False
        self.txt_mensagem.focus = True
    def adicionar_mensagem(self, texto, autor="usuario"):
        if autor == "usuario":
            cor = "[color=1E90FF][b]Você:[/b][/color]"
        else:
            cor = "[color=32CD32][b]Assistente:[/b][/color]"

        lbl = Label(
            text=f"{cor}\n{texto}",
            markup=True,
            size_hint_x=1,
            size_hint_y=None,
            valign='top',
            halign='left',
            font_size='14sp'
        )

        lbl.bind(width=lambda instance, val: setattr(instance, 'text_size', (val - 10, None)))
        lbl.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1] + 10))

        self.chat_history.add_widget(lbl)
        self.scroll.scroll_to(lbl)