#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código!


from enlace import *
from enlaceRx import *
import time
import numpy as np
import struct
import time

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "/dev/tty.usbmodem2101" # Mac    (variacao de)
#serialName = "COM3"                  # Windows(variacao de)  detectar sua porta e substituir aqui


def main():
    try:
        print("Iniciou o main")

        com1 = enlace(serialName)

        com1.enable()

        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)

        print("Abriu a comunicação")

        def verificar_datagrama(self,datagrama, eop_esperado=b'\xFF\xFF\xFF'):
            if len(datagrama) < 15:
                return False, "Datagrama muito curto!"

            header = datagrama[:12]
            eop = datagrama[-3:]

            if eop != eop_esperado:
                return False, "EOP inválido!"

            if header[5]+15 != len(datagrama):
                return False

            if self.num_pacote - self.total_pacotes != 1:
                return False, "Algum pacote foi perdido no meio do caminho"
            else:
                self.total_pacotes += 1

            return True, header

        size = struct.unpack('<f', size)[0]

        pacote, _ = com1.getData(com1.rx.getBufferLen())

        verificar_datagrama(pacote)

        print(size)

        for i in range(int(size)):

            numero, _ = com1.getData(4)

            numero = struct.unpack('<f', numero)[0]

            print(numero)

            soma += numero


        print(f"{soma:.6f}")

        bytesBuffer = struct.pack("f", soma)
        com1.sendData(bytesBuffer)


        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()


if __name__ == "__main__":
    main()

class datagrama:
    def __init__(self, tipo , info_payload , data , eop= b'\xFF\xFF\xFF'):

        self.tipo=tipo                               # Handshake, Resposta do servidor, Mensagem de Dados, ACK (confirmação), Timeout, Erro
        self.total_pacotes=0                         # Total de pacotes recebidos
        self.num_pacote=0                            # Número do pacote
        self.info_payload=info_payload               # Tamanho do payload
        self.data=data                               # Payload
        self.eop=eop

        self.h1=0
        self.h2=0
        self.h6=0
        self.h7=0
        self.h8=0
        self.h9=0
        self.h10=0
        self.h11=0


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
        header = self.monta_header()
        datagrama = header + self.data + self.eop
        return datagrama

    def verificar_datagrama(self,datagrama, eop_esperado=b'\xFF\xFF\xFF'):
        if len(datagrama) < 15:
            return False, "Datagrama muito curto!"

        header = datagrama[:12]
        eop = datagrama[-3:]

        if eop != eop_esperado:
            return False, "EOP inválido!"

        if header[5]+15 != len(datagrama):
            return False

        if self.num_pacote - self.total_pacotes != 1:
            return False, "Algum pacote foi perdido no meio do caminho"
        else:
            self.total_pacotes += 1

        return True, header