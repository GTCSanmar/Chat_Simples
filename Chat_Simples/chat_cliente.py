import socket
import struct
import threading
import sys
import os
import time

MULTICAST_GROUP = '224.1.1.1'
PORT = 5007
TTL = 1 
BUFFER_SIZE = 1024

NICKNAME = "Usuário Desconhecido" 


def receive_messages():
    """
    Thread dedicada a escutar e imprimir mensagens do grupo Multicast.
    """
    
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        receiver_socket.bind(('', PORT))
    except socket.error as e:
        print(f"Erro ao vincular a porta: {e}")
        sys.exit(1)
    
    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    receiver_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # Esta mensagem só aparecerá após o usuário digitar o nickname
    print(f"[*] Escutando em {MULTICAST_GROUP}:{PORT}...")

    while True:
        try:
            data, address = receiver_socket.recvfrom(BUFFER_SIZE)
            message = data.decode('utf-8')
            
            # Se a mensagem não for vazia, imprime
            if message:
                # Usa sys.stdout.write e flush para não interferir no input do usuário
                sys.stdout.write(f"\n[{address[0]}] {message}\n{NICKNAME}> ")
                sys.stdout.flush()
            
        except:
            break


def send_messages(sender_socket):
    """
    Lida com a entrada do usuário e envia mensagens para o grupo Multicast.
    """
    
    print("------------------------------------------------------------------")
    print(f"[*] Você entrou no chat como: {NICKNAME}")
    print(f"[*] Digite 'quit' ou 'sair' para encerrar.")
    print("------------------------------------------------------------------")
    
    multicast_address = (MULTICAST_GROUP, PORT)

    while True:
        try:
            message = input(f"{NICKNAME}> ")
            
            if message.lower() in ('quit', 'sair'):
                break
            
            full_message = f"{NICKNAME}: {message}"
            
            sender_socket.sendto(full_message.encode('utf-8'), multicast_address)

        except EOFError:
            break
        except Exception as e:
            print(f"\n[!] Erro de envio: {e}")
            break

def main_chat_client():
    """
    Função principal que pede o nickname, configura os sockets e as threads.
    """
    global NICKNAME 
    
    # --- 1. Pede o nickname ao usuário ---
    default_nickname = os.environ.get('USER') or os.environ.get('USERNAME') or 'Usuario'
    
    chosen_nickname = input(f"Digite seu nome de usuário (padrão: {default_nickname}): ").strip()
    
    if chosen_nickname:
        NICKNAME = chosen_nickname
    else:
        NICKNAME = default_nickname
        
    print(f"Iniciando chat como {NICKNAME}...")
    
    # 2. Configura Sockets
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sender_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL)
    
    # 3. Inicia a thread de RECEPÇÃO
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()
    
    time.sleep(0.5) 

    send_messages(sender_socket)
    
    print("\nEncerrando o chat...")
    sender_socket.close()
    os._exit(0)

if __name__ == "__main__":

    main_chat_client()
