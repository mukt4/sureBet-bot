#!/usr/local/bin/python
# coding: latin-1

# Colas que necesitaremos para los hilos
# Primera: Cola en la que el hilo de codere escribe al hilo de bet
# Segunda: Cola en la que bet escribe a principal
# Tercera: Cola en la que codere escribe a principal
# Cuarta: Cola en la que principal escribe a bet
# Quinta: Cola en la que principal escribe a codere
# Por si evento ha acabado //button[@class="alert-button alert-button-md alert-button-default alert-button-default-md"]/span

import queue

from stats.estadistica import comprobar_cotizaciones
from crawler.tenis_bet import ThreadBet
from crawler.tenis_codere import ThreadCodere
from time import sleep
from difflib import SequenceMatcher

# Funcion que devuelve la similitud entre una cadena y otra
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# Realizar esperas entre solicitudes
if __name__ == "__main__":
	cola1 = Queue.Queue()
	cola2 = Queue.Queue()
	cola3 = Queue.Queue()
	cola4 = Queue.Queue()
	cola5 = Queue.Queue()
	cola6 = Queue.Queue()

	maximo = raw_input("INTRODUCE EL DINERO MAXIMO A APOSTAR: ")

	codere = ThreadCodere(cola1, cola2, cola5, cola6)
	bet = ThreadBet(cola1, cola2, cola3, cola4)
	
	codere.start()
	bet.start()
	# Siempre bet es el primero en comprobar para obtener valor redondo
	# Cola 4 es bet y cola 6 es codere
	while True:
		datos_bet = cola3.get()
		datos_codere = cola5.get()
		cotizaciones = comprobar_cotizaciones(datos_bet[0], datos_codere[1], maximo)
		if (cotizaciones[0] == True):
			try:
				a = cotizaciones[1]
				b = cotizaciones[2]
				cola4.put([True, a, 0])
				cola6.put([True, 0, b])
				print("SURE BET ENCONTRADA")
				fichero = open("SURE_BET/sure_completo.txt", "a")
				fichero.write(str(a + b) + " " + str(maximo)+ "\n")
				fichero.close()
			except IndexError as e:
				cola4.put([False])
				cola6.put([False])
		else:
			cotizaciones = comprobar_cotizaciones(datos_bet[1], datos_codere[0], 10)
			if (cotizaciones[0] == True):
				try:
					a = cotizaciones[1]
					b = cotizaciones[2]
					cola4.put([True, 0, a])
					cola6.put([True, b, 0])
					print("SURE BET ENCONTRADA")
					fichero = open("SURE_BET/sure_completo.txt", "a")
					fichero.write(str(a + b) + " " + str(maximo)+ "\n")
					fichero.close()
				except IndexError as e:
					cola4.put([False])
					cola6.put([False])
			else:
				cola4.put([False])
				cola6.put([False])

	fichero.close()
	codere.parar()
	bet.parar()