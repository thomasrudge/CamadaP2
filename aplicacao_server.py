from enlace import *
from enlaceRx import *
import time
import struct
import random

serialName = "/dev/cu.usbmodem2101"

class datagrama:
    def __init__(self, tipo, info_payload, data, eop=b'\xFF\xFF\xFF'):
        self.tipo = tipo
        self.total_pacotes = 0
        self.num_pacote = 0
        self.info_payload = info_payload
        self.data = data
        self.eop = eop
        self.h1 = self.h2 = self.h6 = self.h7 = self.h8 = self.h9 = self.h10 = self.h11 = 0

    def monta_header(self):
        header = bytearray(12)
        header[0] = self.tipo
        header[1] = self.h1
        header[2] = self.h2
        header[3] = self.total_pacotes
        header[4] = self.num_pacote + 1
        header[5] = self.info_payload
        header[6] = self.h6
        header[7] = self.h7
        header[8] = self.h8
        header[9] = self.h9
        header[10] = self.h10
        header[11] = self.h11
        return bytes(header)

    def monta_datagrama(self):
        return self.monta_header() + self.data + self.eop

erro_ocorrido = False

def main():

    mensagens = {
        0: ["Handshake", "Handshake recebido", "Inconsistência no handshake!", datagrama(0, 0, b"")],
        1: ["Resposta do Servidor", "Resposta do servidor recebida", "Inconsistência na resposta do servidor!", datagrama(1, 8, b"Recebido")],
        2: ["Mensagem de Dados", "Mensagem de Dados recebida", "Inconsistência na mensagem de dados!", datagrama(2, 13, b"oi, tudo bem?")],
        3: ["ACK", "ACK recebido", "Inconsistência no ACK!", datagrama(3, 0, b"")],
        4: ["Timeout", "Timeout recebido", "Inconsistência no Timeout!", datagrama(4, 0, b"")],
        5: ["Erro", "Erro recebido", "Inconsistência no Erro!", datagrama(5, 0, b"")]
    }
    
    pacotes = {
        1: datagrama(1, 1, b"1"),
        2: datagrama(1, 1, b"2"),
        3: datagrama(1, 1, b"3"),
        4: datagrama(1, 1, b"4"),
        5: datagrama(1, 1, b"5"),
        6: datagrama(1, 1, b"6"),
        7: datagrama(1, 1, b"7"),
        8: datagrama(1, 1, b"8"),
        9: datagrama(1, 1, b"9"),
    }

    global erro_ocorrido

    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.1)
        print("Abriu a comunicação")

        def registrar_log(direcao, header, payload):
            timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
            tipo_msg = header[0]
            total_bytes = len(header) + len(payload) + 3
            pacote_num = header[4]
            total_pacotes = header[3]
            crc_val = int.from_bytes(header[10:12], 'big')
            line = f"{timestamp} / {direcao} / {tipo_msg} / {total_bytes} / {pacote_num} / {total_pacotes} / {crc_val:04X}\n"
            with open("log_server.txt", "a") as f:
                f.write(line)

        def aguardar_dados(qtd, tempo_max=5):
            inicio = time.time()

            while time.time() - inicio < tempo_max:
                if com1.rx.getBufferLen() >= qtd:
                    return True
                
                time.sleep(0.01)

            return False

        def tipo_pacote(h, payload, eop, eop_esp=b'\xFF\xFF\xFF'):
            if h[4] - h[3] != 1 or eop != eop_esp:
                print("Número de pacote ou EOP inválido!")
                return None

            print(f'Recebi um {mensagens[h[0]][0]} com sucesso!')

            if h[0] != 0:
                print(f"{payload}")

            registrar_log("Recebido", h, payload)

            if len(payload) != h[5]:
                print("Erro: tamanho do payload incorreto")
                return None

            return pacotes[random.randint(1, 9)]

        def verificar_datagrama(h, eop_esp=b'\xFF\xFF\xFF'):
            global erro_ocorrido

            if len(h) != 12:
                print("Header Errado!")
                erro_ocorrido = True
                return None
            
            if not aguardar_dados(h[5], 5):
                print("Erro de timeout no payload")
                erro_ocorrido = True
                return None
            
            payload, _ = com1.getData(h[5]) if h[5] > 0 else (b"", 0)

            if not aguardar_dados(3, 5):
                print("Erro de timeout no eop")
                erro_ocorrido = True
                return None
            
            eop, _ = com1.getData(3)
            resp = tipo_pacote(h, payload, eop, eop_esp)

            if resp is None:
                print("Inconsistência detectada. Abortando comunicação.")
                erro_ocorrido = True
                return None
            
            com1.sendData(resp.monta_datagrama())

            return h, payload, eop

        for _ in range(6):
            if erro_ocorrido:
                break

            if not aguardar_dados(12, 5):
                print("Timeout na leitura do header")
                erro_ocorrido = True
                break

            header, _ = com1.getData(12)
            
            if verificar_datagrama(header) is None:
                print("Abortando comunicação devido a inconsistência.")
                break

        print("-------------------------")
        print("Comunicação encerrada")
        com1.disable()

    except Exception as e:
        print("ops! :-\\", e)
        com1.disable()

if __name__ == "__main__":
    main()