from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import gerar_resposta_ia

class ChatIAView(APIView):
    """
    Endpoint que recebe a mensagem do app celular (Kivy)
    e devolve a resposta gerada pela IA.
    """
    def post(self, request):
        mensagem = request.data.get('mensagem', '').strip()

        if not mensagem:
            return Response(
                {"erro": "Nenhuma mensagem enviada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resposta_ia = gerar_resposta_ia(mensagem)

        return Response(
            {"resposta": resposta_ia},
            status=status.HTTP_200_OK
        )