#!/usr/bin/env python3
import socket
import threading
import sys
import json
import time
import random

# Configurarea conexiunii
LOCAL_IP = '127.0.0.1'    # Adresa localhost pentru macOS
BASE_PORT = 45000         # Port de bază
PORT_RANGE = 10           # Utilizăm porturile 45000-45009
BUFFER_SIZE = 2048        # Dimensiunea buffer-ului

class UDPChat:
    def __init__(self, username):
        self.username = username
        self.running = True
        self.clients = {}  # username -> [port, last_seen_time]
        self.setup_socket()
        
    def setup_socket(self):
        """Configurează socket-ul UDP"""
        try:
            # Creează un socket UDP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Încearcă să asocieze un port disponibil din interval
            port_assigned = False
            for port in range(BASE_PORT, BASE_PORT + PORT_RANGE):
                try:
                    self.socket.bind((LOCAL_IP, port))
                    self.port = port
                    port_assigned = True
                    break
                except OSError:
                    continue
                    
            if not port_assigned:
                print("Nu s-a putut găsi un port disponibil. Încercați din nou.")
                sys.exit(1)
                
            print(f"Chat inițializat cu succes pe portul {self.port}")
        except Exception as e:
            print(f"Eroare la configurarea socket-ului: {e}")
            sys.exit(1)
    
    def broadcast_message(self, data):
        """Trimite mesajul către toate porturile din interval"""
        for port in range(BASE_PORT, BASE_PORT + PORT_RANGE):
            if port != self.port:  # Nu trimite către sine
                try:
                    self.socket.sendto(data, (LOCAL_IP, port))
                except:
                    pass
    
    def send_message(self, message_type, content, recipient="ALL"):
        """Creează și trimite un mesaj"""
        try:
            # Creează structura mesajului
            message = {
                'type': message_type,
                'sender': self.username,
                'sender_port': self.port,
                'recipient': recipient,
                'content': content,
                'timestamp': time.time()
            }
            
            # Codifică mesajul ca JSON
            data = json.dumps(message).encode('utf-8')
            
            # Trimite mesajul către toate porturile
            self.broadcast_message(data)
            return True
        except Exception as e:
            print(f"Eroare la trimiterea mesajului: {e}")
            return False
    
    def receive_messages(self):
        """Primește și procesează mesaje"""
        self.socket.settimeout(0.5)  # Timeout pentru a permite verificări periodice
        
        while self.running:
            try:
                # Primește date
                data, addr = self.socket.recvfrom(BUFFER_SIZE)
                
                # Decodează și procesează
                try:
                    message = json.loads(data.decode('utf-8'))
                    
                    # Verifică dacă mesajul are toate câmpurile necesare
                    required_fields = ['type', 'sender', 'sender_port', 'recipient', 'content']
                    if not all(field in message for field in required_fields):
                        continue
                    
                    # Ignoră propriile mesaje
                    sender = message['sender']
                    sender_port = message['sender_port']
                    
                    if sender == self.username and sender_port == self.port:
                        continue
                    
                    # Actualizează lista de clienți activi
                    if sender not in self.clients:
                        print(f"\nUtilizator nou: {sender} (port: {sender_port})")
                        print("> ", end='', flush=True)
                    
                    # Actualizează informațiile despre client
                    self.clients[sender] = [sender_port, time.time()]
                    
                    # Procesează mesajul în funcție de tip
                    msg_type = message['type']
                    
                    if msg_type == 'HELLO':
                        # Răspunde cu un mesaj de confirmare
                        time.sleep(0.1)  # Mică întârziere pentru a evita coliziuni
                        self.send_message('HELLO_ACK', "Sunt aici!")
                    
                    elif msg_type == 'GENERAL':
                        if message['recipient'] == 'ALL':
                            print(f"\n[GENERAL] {sender}: {message['content']}")
                            print("> ", end='', flush=True)
                    
                    elif msg_type == 'PRIVATE':
                        if message['recipient'] == self.username:
                            print(f"\n[PRIVAT] {sender}: {message['content']}")
                            print("> ", end='', flush=True)
                    
                    elif msg_type == 'BYE':
                        if sender in self.clients:
                            del self.clients[sender]
                            print(f"\n{sender} a părăsit conversația")
                            print("> ", end='', flush=True)
                
                except json.JSONDecodeError:
                    pass  # Ignoră mesajele care nu sunt în format JSON valid
                except Exception as e:
                    print(f"\nEroare la procesarea mesajului: {e}")
                    print("> ", end='', flush=True)
            
            except socket.timeout:
                pass  # Timeout normal, continuă bucla
            except Exception as e:
                if self.running:
                    print(f"\nEroare la primirea mesajelor: {e}")
                    print("> ", end='', flush=True)
    
    def heartbeat_thread(self):
        """Trimite periodic mesaje pentru a menține prezența"""
        last_heartbeat = 0
        last_cleanup = 0
        
        while self.running:
            current_time = time.time()
            
            # Trimite un heartbeat la fiecare 5 secunde
            if current_time - last_heartbeat > 5:
                self.send_message('HEARTBEAT', "Sunt activ")
                last_heartbeat = current_time
            
            # Curăță clienții inactivi la fiecare 15 secunde
            if current_time - last_cleanup > 15:
                inactive_threshold = current_time - 30  # 30 secunde fără activitate = inactiv
                inactive_clients = [username for username, [_, last_seen] in self.clients.items() 
                                  if last_seen < inactive_threshold]
                
                for username in inactive_clients:
                    del self.clients[username]
                
                last_cleanup = current_time
            
            time.sleep(1)
    
    def start(self):
        """Pornește aplicația de chat"""
        print(f"Pornirea aplicației UDP Chat ca '{self.username}'...")
        
        # Pornește thread-ul pentru primirea mesajelor
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Pornește thread-ul pentru heartbeat
        heartbeat_thread = threading.Thread(target=self.heartbeat_thread)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()
        
        # Anunță prezența inițială de câteva ori
        for _ in range(5):
            self.send_message('HELLO', "S-a alăturat conversației")
            time.sleep(0.2)
        
        # Așteaptă descoperirea altor utilizatori
        print("Se caută alți utilizatori...")
        time.sleep(2)
        
        # Bucla principală
        try:
            print("\nBine ați venit la UDP Chat!")
            print("Comenzi:")
            print("  /p <numeutilizator> <mesaj> - Trimite un mesaj privat")
            print("  /list - Afișează utilizatorii conectați")
            print("  /refresh - Actualizează lista de utilizatori")
            print("  /quit - Ieși din conversație")
            print()
            
            while True:
                user_input = input("> ")
                
                if not user_input.strip():
                    continue
                
                if user_input.strip().lower() == '/quit':
                    break
                elif user_input.startswith('/p '):
                    # Mesaj privat
                    parts = user_input[3:].strip().split(' ', 1)
                    if len(parts) != 2:
                        print("Utilizare: /p <numeutilizator> <mesaj>")
                        continue
                    
                    recipient, message = parts
                    
                    if recipient not in self.clients:
                        print(f"Utilizatorul {recipient} nu este conectat")
                        continue
                        
                    self.send_message('PRIVATE', message, recipient)
                    print(f"Mesaj privat trimis către {recipient}")
                    
                elif user_input.strip().lower() == '/list':
                    if not self.clients:
                        print("\nNu există alți utilizatori conectați")
                    else:
                        print("\nUtilizatori conectați:")
                        for username, [port, _] in self.clients.items():
                            print(f"- {username} (port: {port})")
                    print()
                    
                elif user_input.strip().lower() == '/refresh':
                    print("\nSe actualizează lista de utilizatori...")
                    for _ in range(3):
                        self.send_message('HELLO', "Actualizare")
                        time.sleep(0.2)
                    
                    time.sleep(1)  # Așteaptă răspunsuri
                    
                    if not self.clients:
                        print("Nu există alți utilizatori conectați")
                    else:
                        print("Utilizatori conectați:")
                        for username, [port, _] in self.clients.items():
                            print(f"- {username} (port: {port})")
                    print()
                    
                else:
                    # Mesaj general
                    self.send_message('GENERAL', user_input)
        
        except KeyboardInterrupt:
            print("\nSe închide aplicația...")
        except Exception as e:
            print(f"Eroare în bucla principală: {e}")
        finally:
            self.running = False
            self.send_message('BYE', "A părăsit conversația")
            time.sleep(0.5)
            self.socket.close()
            print("Aplicația UDP Chat a fost închisă.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilizare: python udp_chat.py <numeutilizator>")
        sys.exit(1)
    
    # Inițializare și pornire chat
    username = sys.argv[1]
    chat = UDPChat(username)
    chat.start()