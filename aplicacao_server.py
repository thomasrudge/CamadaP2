from enlace import *
from enlaceRx import *
import time
import struct

serialName = "/dev/cu.usbmodem1101"

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

    global erro_ocorrido

    try:
        print("Iniciou o main")
        com1 = enlace(serialName)
        com1.enable()
        com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(0.1)
        print("Abriu a comunicação")

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
            
            if h[0] == 0:
                print("Handshake recebido")

                if h[5] != 0:
                    print("Inconsistência no handshake!")
                    return None
                
                return datagrama(1, 0, b"")
            
            # Não usado no server
            elif h[0] == 1:
                print("Resposta do servidor recebida")
                return datagrama(2, 13, b"oi, tudo bem?")
            
            elif h[0] == 2:
                print("Mensagem de Dados recebida")

                if len(payload) != h[5]:
                    print("Erro: tamanho do payload incorreto")
                    return None
                
                return datagrama(3, 0, b"")
            
            # Não usado no server
            elif h[0] == 3:
                print("ACK recebido")

                return datagrama(4, 0, b"")
            
            elif h[0] == 4:
                print("Timeout recebido")

                return datagrama(5, 0, b"")
            
            else:
                print("Tipo de pacote desconhecido ou erro")
                return None

        def verificar_datagrama(h, eop_esp=b'\xFF\xFF\xFF'):
            global erro_ocorrido
            if len(h) != 12:
                print("Header Errado!")
                erro_ocorrido = True
                return None
            
            tam = h[5]

            if not aguardar_dados(tam, 5):
                print("Erro de timeout no payload")
                erro_ocorrido = True
                return None
            
            payload, _ = com1.getData(tam) if tam > 0 else (b"", 0)
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

        for _ in range(3):
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
