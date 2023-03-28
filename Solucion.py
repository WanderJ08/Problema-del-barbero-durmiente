import threading 
import time
import random
import queue ##El módulo estándar Queue o queue  permite crear y trabajar con colas de manera sencilla
            ##Es generalmente utilizado en programas multi-hilo, ya que provee una forma de intercambiar información entre threads de manera segura.

BARBEROS = 1 ##cantidad de barberos, es modificable
ESPERAS= 1 ## se usara un multiplo de random.random() para la que clientes lleguen
ASIENTOS= 4 ##cantidad de asientos, es modificable
CLIENTES = 60 ##cantidad de clientes, es modificable

def espera():##simula la llegada de clientes a tiempo al azar
    time.sleep(ESPERAS * random.random())

class Barbero(threading.Thread):
    condicion = threading.Condition() ##Con esto se despierta o duerme el barbero
    alto_completo = threading.Event() ##Esto sirve para cuando todos los clientes han sido atendidos

    def __init__(self, ID):
        super().__init__()
        self.ID = ID    ##establece el id del barbero en caso de agregar mas de 1


    def run(self):
        while True:
            try: ##usamos try y except porque es mejor que revisar el tamaño de queue, queue.qsize no es seguro con hilos
                cliente_actual = sala_espera.get(block=False) ## block-false para que el hilo no espere o bloquee para obtener un espacio
            except queue.Empty: #se lanza cuando sala_espera está llena
                if self.alto_completo.is_set(): #alto_completo se activa solo cuando clientes han sido atendidos completamente
                    return
                
                print(f"\n El barbero {self.ID} esta durmiendo:... Zzz... Zzz... ") ##Si no hay clientes se va a dormir el barbero
                with self.condicion:
                    self.condicion.wait()##con esta linea de codigo el barbero duerme y espera a que el cliente lo despierte
            else:
                cliente_actual.cortar(self.ID) ##con esta linea de codigo el barbero corta el cabello de los clientes

class Cliente(threading.Thread):
    DURACION_CORTE= 5

    def __init__(self, ID):
        super().__init__()
        self.ID = ID

    def corte(self): ##Esta funcion simula el corte de cabello
        time.sleep(self.DURACION_CORTE * random.random())

    def cortar(self, id_barbero): ##se hace un llamado desde el hilo barbero
        print(f"\n El barbero {id_barbero} está cortando el cabello del cliente {self.ID}")
        self.corte() ## esta obteniendo "get" un corte
        print(f"\n El barbero {id_barbero} terminó de cortar el cabello al cliente {self.ID}")
        self.atendido.set() ## "set" fue atendido para que el cliente deje la barberia

    def run(self):
        self.atendido = threading.Event()

        try:## Esto revisa si hay espacio en la sala_espera
            sala_espera.put(self, block=False)
        except queue.Full:## si no hay espacio en la sala_espera el cliente se va
            print(f"\n La sala de espera esta llena, {self.ID} se fue...")
            return
        
        print(f"\n El cliente {self.ID} se sentó en la sala de espera.")
        with Barbero.condicion:
            Barbero.condicion.notify(1)#este segmento de codigo despierta al barbero

        self.atendido.wait()#espera para obtener "get" un corte y se retira


if __name__ == "__main__":
    TODOS_CLIENTES = [] ##la lista de todos los clientes en el dia
    sala_espera = queue.Queue(ASIENTOS)# tamaño maximo de asientos, esto eliminar la necesidad de Queue.qsize()

    for i in range(BARBEROS):## este segmento de codigo crea el hilo barbero
        hilo_barbero = Barbero(i)
        hilo_barbero.start()

    for i in range(CLIENTES):## este segmento de codigo crea el hilo cliente
        espera()
        cliente = Cliente(i)
        TODOS_CLIENTES.append(cliente)
        cliente.start()

    for cliente in TODOS_CLIENTES:
        cliente.join()#esto espera la salida de todos los clientes

    time.sleep(0.1)# se coloca este tiempo con time.sleep para darle tiempo al barbero para limpiar tras el cliente final
    Barbero.alto_completo.set()##este segmento de codigo permite que se pueda finalizar el trabajo del barbero
    with Barbero.condicion:
        Barbero.condicion.notify_all()

    print("\n La barbería está cerrada.")

