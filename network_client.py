import os
import json
import time
import requests
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_private_key

#Var de Ambiente do Docker
NICK = os.getenv("ID", "fadf")
PRIVATE_KEY_B64 = os.getenv("PRIVATE_KEY")
PUBLIC_KEY_B64 = os.getenv("PUBLIC_KEY")
#URL
TARGET_URL = os.getenv("URL", "http://localhost:5000/api/sudoku/1")

#Inicialização da Chave Privada
private_key = None
if PRIVATE_KEY_B64:
    try:
        der_data = base64.b64decode(PRIVATE_KEY_B64)
        private_key = load_der_private_key(der_data, password=None)
    except Exception as e:
        print(f"Erro ao carregar a chave privada: {e}")

def sign_nick():
    """Gera a assinatura ECDSA"""
    if not private_key:
        return "assinatura_desabilitada_sem_chave"
        
    signature = private_key.sign(
        NICK.encode('utf-8'),
        ec.ECDSA(hashes.SHA256())
    )
    return signature.hex()

def get_initial_board():
    """Faz o GET na URL"""
    try:
        response = requests.get(TARGET_URL, timeout=10)
        
        if response.status_code == 200:
            run_dto = response.json()
            board_2d = run_dto.get("root", {}).get("value", {}).get("board", [])
            
            if not board_2d:
                print("Erro: Estrutura do tabuleiro não encontrada.")
                return None
                
            return [item for sublist in board_2d for item in sublist]
            
        else:
            print(f"Erro ao buscar tabuleiro. Status: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Falha de conexão com a API no GET inicial: {e}")
        return None

def send_progress(clean_board_matrix):
    signature_hex = sign_nick()
    
    dto = {
        "board": clean_board_matrix,
        "signature": {
            "identifier": signature_hex,
            "key": PUBLIC_KEY_B64
        }
    }
    
    backoff_time = 2 
    while True:
        try:
            #timeout  5sec --> 3sec
            response = requests.post(TARGET_URL, json=dto, timeout=3)
            
            if response.status_code in [200, 201, 202]:
                return True
            elif response.status_code == 429:
                print(f"Erro 429. Aguardando {backoff_time}s...")
                time.sleep(backoff_time)
                #Backoff limit 60 seconds
                backoff_time = min(backoff_time * 2, 60)
                continue
            else:
                print(f"Erro: {response.status_code}. Retentando em {backoff_time}s...")
                time.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, 60)
                
        except requests.exceptions.RequestException as e:
            print(f"Falha de conexão no POST: {e}. Retentando em {backoff_time}s...")
            time.sleep(backoff_time)
            backoff_time = min(backoff_time * 2, 60)