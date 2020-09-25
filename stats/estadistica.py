import random
import time
import math

from time import sleep
from difflib import SequenceMatcher
from math import ceil

def test_estadistica():
	print("Introuduce la cantidad maxima que se va a apostar")
	maximo = float(raw_input())

	while True:
		casa_a = float(random.randrange(100, 400))/100
		casa_b = float(random.randrange(100, 400))/100

		print("Cotizacion casa a: " + str(casa_a))
		print("Cotizacion casa b: " + str(casa_b))
		total = casa_a + casa_b

		# Primera forma de calcular sure bet, se equivoca de vez en cuando
		print("-------Metodo A-------")
		if total > 4:
			print("\tSe pueden realizar apuestas con estas cotizaciones")
			print("\tCASA A--> " + str(casa_a) + " CASA B--> " + str(casa_b))
			# Hay que tener en cuenta que en la casa a solo se pueden realizar apuestas redondas
			porcentaje_a = casa_a/total
			porcentaje_b = casa_b/total
			dinero_a = porcentaje_b * maximo
			dinero_b = porcentaje_a * maximo
			total_apostado = dinero_a + dinero_b

			print("\tDinero a apostar en a: " + str(dinero_a))
			print("\tDinero a apostar en b: " + str(dinero_b))
			print("\tTotal de dinero apostado: " + str(total_apostado))
			ganancia_a = casa_a * dinero_a
			ganancia_b = casa_b * dinero_b
			porcentaje_ganancia = ganancia_a/maximo
			print("\tGanancia total en a: " + str(ganancia_a))
			print("\tGanancia total en b: " + str(ganancia_b))
			print("\tPorcentaje de ganancia: " + str(porcentaje_ganancia))

		else:
			print("\tNo se pueden realizar apuestas con estas cotizaciones")
			print("\tCASA A--> " + str(casa_a) + " CASA B--> " + str(casa_b))

		print("\n----->Analizando apuesta con el metodo B\n")

		# Segunda forma de calcular sure bet
		print("-------Metodo B-------")
		check = (1/casa_a) + (1/casa_b)

		if check < 1:
			print("\tSe pueden realizar apuestas con estas cotizaciones")
			print("\tCASA A--> " + str(casa_a) + " CASA B--> " + str(casa_b))
			porcentaje_ganancia_aux = 1 - check
			print("\tSe estima porcentaje de ganancia de " + str(porcentaje_ganancia_aux))
			apuesta_a = maximo/casa_a
			apuesta_a = ceil(apuesta_a)
			apuesta_b = maximo/casa_b
			print("\tDinero a apostar en A: " + str(apuesta_a))
			print("\tDinero a apostar en B: " + str(apuesta_b))
			total_apostado_aux = apuesta_a + apuesta_b
			print("\tDinero total apostado: " + str(total_apostado_aux))
			ganancia_a_aux = apuesta_a * casa_a
			ganancia_b_aux = apuesta_b * casa_b
			# Aqui se podria realizar comprobacion de emergencia para comprobar el redondeo
			print("\tGanancia total en a: " + str(ganancia_a_aux))
			print("\tGanancia total en b: " + str(ganancia_b_aux))
		else:
			print("\tNo se pueden realizar apuestas con estas cotizaciones")
			print("\tCASA A--> " + str(casa_a) + " CASA B--> " + str(casa_b))

		print("\n--------------------> Pasamos a analizar siguiente apuesta\n")

		sleep(1)

	# El metodo b es el bueno y deja redondear

# Devuelve true si se puede apostar y false si no
# Devolver tambien si es true cuanto se deberia apostar en cada elemento
# Pasarlo en forma de lista
# Primer elemento contiene True o False
# Segundo contiene cantidad casa A
# Tercero contiene cantidad casa B
# Casa A es bet
# Casa B es codere
# Cambiar esta funcion a lo que hemos hablado
def comprobar_cotizaciones(cotizacion_a, cotizacion_b, maximo):
	lista = []
	try:
		print("Cotizaciones recibidas en estadistica-> [" + str(cotizacion_a) + "-" + str(cotizacion_b) + "]")
		a = float(cotizacion_a.replace(",", "."))
		b = float(cotizacion_b.replace(",", "."))
		x = (1/a) + (1/b)
		print("Valor sure bet->" + str(x))
		#0.95
		if (x < 0.98 and x > 0.75):
			lista.append(True)
			valor_a = round(maximo/a,2)
			valor_b = round(maximo/b)
			lista.append(valor_a)
			lista.append(valor_b)
			return lista
		else:
			lista.append(False)
			return lista
	except:
		lista.append(False)
		return lista

# Funcion que devuelve la similitud entre una cadena y otra
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()




	