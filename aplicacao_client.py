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

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)  detectar sua porta e substituir aqui


def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()

        time.sleep(.2)

        com1.sendData(b'00')

        print("mandei")

        time.sleep(1)
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        
        
                  
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são um array bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        
       ## imageR = "japao.png"
       # imageW = "copiaRecebida5.png"

       # print("Carregando imagem para transmissao :")
        #print(" - {}".format(imageR))
        #print("---------------------")
        
        txBuffer = [6, 16.010101,10.131313,24.151515 , 16.939393 , 10.000001 , 32.141414]
        bytesBuffer = b"".join(struct.pack("f", valor) for valor in txBuffer)
        com1.sendData(bytesBuffer)

        #for i in range(len(txBuffer)):
         #   time.sleep(0.05)
          #  com1.sendData(txBuffer[i])
        #txBuffer = b'\x12\x13\xAA\x01'  #isso é um array de bytes. apenas um exemplo para teste. Deverá ser substutuido pelo 
        #array correspondente à imagem
       
        print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
       
            
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmita arrays de bytes!
        #txBuffer = b'\xAA\x12\xFF'    
        print("Transmissao vai comecar! ")
        #com1.sendData(np.asarray(txBuffer))  #as array apenas como boa pratica para casos de ter uma outra forma de dados
    
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        while com1.tx.threadMutex == True:
            time.sleep(0.01)
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.]



        tempo_antes = time.time()
        print("A recepcao vai comecar! ")
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
        #com1.tx.transLen
      
        #acesso aos bytes recebidos
        txLen = len(txBuffer)

        tempo_antes = time.time()
        rxBuffer = 0
        #time.sleep(5)
        

        recebido = False

        while time.time() - tempo_antes < 5:
            tam = com1.rx.getBufferLen()
            if tam == 4:
                recebido = True
                break

        #time.sleep(5)



        if recebido == True:
            rxBuffer, nRx = com1.getData(4)
            print("recebeu {} bytes" .format(len(rxBuffer)))
            rxBuffer = struct.unpack('<f',rxBuffer)[0]

            print(rxBuffer)

        else:
            print("Nao recebi nada")
                
            
        



        


        #print(rxBuffer)

       
        #print(" - {}".format(imageW))
        #f = open(imageW , 'wb')
        #f.write(rxBuffer)

        
        

        
        
        #apenas para teste dos 4 bytes exemplo. NO caso da imagem devera ser retirado para nao poluir...
    #    for i in range(len(rxBuffer)):
    #        print("recebeu {}" .format(rxBuffer[i]))
        

            
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
