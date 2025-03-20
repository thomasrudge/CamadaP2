#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import struct
import binascii

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"  

class datagrama:
    def __init__(self, tipo , info_payload , data , eop= b'\xFF\xFF\xFF'):

        self.tipo=tipo                               # Handshake, Resposta do servidor, Mensagem de Dados, ACK (confirmação), Timeout, Erro
        self.total_pacotes=0                         # Total de pacotes recebidos
        self.num_pacote=0                        # Número do pacote
        self.info_payload=info_payload               # Tamanho do payload
        self.data=data                               # Payload
        self.eop=eop

        self.h1=0
        self.h2=0
        self.h6=0
        self.h7=0
        self.h8=0
        self.h9=0
  
        
        crc = self.calcular_crc()  # valor inteiro de 16 bits
        self.h10 = (crc >> 8) & 0xFF
        self.h11 = crc & 0xFF

        print(f'CRCs enviados: {self.h10} & {self.h11}')



    def monta_header(self):

        header = bytearray(12)

        header[0] = self.tipo
        header[1] = self.h1
        header[2] = self.h2
        header[3] = self.total_pacotes
        header[4] = self.num_pacote+1
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

    def calcular_crc(self: bytes) -> int:
              
        crc = binascii.crc_hqx(self.data, 0)
        
        return crc




def main():

    global payload

    try:
        print("Iniciou o main")

        com1 = enlace(serialName)

        com1.enable()

        time.sleep(.2)

        com1.sendData(b'0')
        
        print("mandei")

        time.sleep(1)

        print("Abriu a comunicação")

        pacotes = []

        
        pacote = datagrama(0, 24, b"Quais pacotes voce quer?")

        bytes_do_pacote = pacote.monta_datagrama()  # retorna um objeto 'bytes'

        com1.sendData(bytes_do_pacote)              # agora sim, enviamos bytes

        print("meu array de bytes tem tamanho {}".format(len(bytes_do_pacote)))

       

        def registrar_log(direcao, header, payload):
            timestamp = time.strftime("%d/%m/%Y %H:%M:%S")
            tipo_msg = header[0]
            total_bytes = len(header) + len(payload) + 3
            pacote_num = header[4]
            total_pacotes = header[3]
            crc_val = int.from_bytes(header[10:12], 'big')
            line = f"{timestamp} / {direcao} / {tipo_msg} / {total_bytes} / {pacote_num} / {total_pacotes} / {crc_val:04X}\n"
            with open("log_client.txt", "a") as f:
                f.write(line)

        registrar_log("Enviado Byte Sacrificio", bytearray(12), "Byte Sacrificio")



        def aguardar_dados(qtd, tempo_max=25):
            inicio = time.time()
            while time.time() - inicio < tempo_max:
                if com1.rx.getBufferLen() >= qtd:
                    return True
                time.sleep(0.01)
            return False

        def verificar_datagrama(header, eop_esperado=b'\xFF\xFF\xFF'):
                
                #print("entrou na funcao vd")]
                payload,_ = com1.getData(1)
                payload = int(payload)
                eop,_ = com1.getData(3)
                registrar_log("Recebido", header, str(payload))

                print(f'Recebi o payload: {payload}')
                print(f'Recebi o eop: {eop}')
                
                erro = False

                

                if len(header) != 12:
                    print("Header Errado!")
                    erro = True


                to = aguardar_dados(0 , 25)

                print(to)
                if to == False:
                    erro=True
                    print("erro de timeout")



               # if header[5] == (com1.rx.getBufferLen()-3):
#
 #                   tamanho_payload = header[5]
#
 #                   
  #                  print(payload)
#
 #                   eop, _ = com1.getData(3)
  #              else:
   #                 print("Tamanho do payload errado")
    #                erro= True
     #               eop = None

                
                if eop != eop_esperado and erro==False:
                    print("EOP inválido!")
                    erro = True

                if header[4] - header[3] != 1:
                    print("Número de pacote inválido!")
                    erro = True

                if erro==False:
                    print("Recebeu o pacote")

               

                if erro == False:
                    return "Tudo certo"
                
                return "Algo Errado"



                

       # txBuffer = [6, 16.010101,10.131313,24.151515 , 16.939393 , 10.000001 , 32.141414]
       # bytesBuffer = b"".join(struct.pack("f", valor) for valor in txBuffer)
        #com1.sendData(bytesBuffer)

       


        print("Transmissao vai comecar! ")

        while com1.tx.threadMutex == True:
            time.sleep(0.01)

        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))




        tempo_antes = time.time()
        print("A recepcao vai comecar! ")

        h1,_ = com1.getData(12)
        payload,_ = com1.getData(1)
        eop1,_ = com1.getData(3)

        payload = int(payload)


        Mensagens = [datagrama(2,4,b"John"),
                     
                     datagrama(2,6,b'Telles'),

                     datagrama(2,7,b'Barbosa'),

                     datagrama(2,6,b"Bastos"),
                     
                     datagrama(2,7,b'Vitinho'),

                     datagrama(2,6,b'Marlon'),

                     datagrama(2,7,b"Gregore"),
                     
                     datagrama(2,6,b'Almada'),

                     datagrama(2,2,b'LH'),

                     datagrama(2,4,b'Igor'),

                     datagrama(2,8,b'Savarino'),

                     ]
        
        
        for i in range(2):

            com1.sendData(Mensagens[payload].monta_datagrama())
            registrar_log("Enviado", pacote.monta_header(), str(payload))
            
            
            print(f'mandei a {i} mensagem')

            if not aguardar_dados(12,25):
                print("Timeout na leitura do header")
                break
            header , _ = com1.getData(12)
            

            verifica_dg = verificar_datagrama(header)

            if verifica_dg == "Algo Errado":
                
                break
                

        


       

        #tempo_antes = time.time()
        #rxBuffer = 0


        #recebido = False

        #while time.time() - tempo_antes < 5:
         #   tam = com1.rx.getBufferLen()
         #   if tam == 4:
         #       recebido = True
         #       break

        #if recebido == True:
        #    rxBuffer, nRx = com1.getData(4)
        #    print("recebeu {} bytes" .format(len(rxBuffer)))
        #    rxBuffer = struct.unpack('<f',rxBuffer)[0]

         #   print(rxBuffer)

        #else:
        #    print("Nao recebi nada")


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