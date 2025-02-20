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

        soma = 0

        size, _ = com1.getData(4)

        size = struct.unpack('<f', size)[0]

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
