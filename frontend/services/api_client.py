import requests

# Endereço local da API Django
API_URL = "http://127.0.0.1:8000/api/chat/"
#API_URL = "https://aasos-backend.onrender.com/api/chat/"

def enviar_mensagem_para_api(mensagem_texto):
    """
    Envia a mensagem do usuário para o backend Django
    e retorna o texto gerado pela IA.
    """
    payload = {"mensagem": mensagem_texto}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=90)
        if response.status_code == 200:
            dados = response.json()
            return dados.get("resposta", "Sem resposta recebida da IA.")
        else:
            return f"Erro no servidor ({response.status_code}): {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Falha na conexão com o servidor: {str(e)}"