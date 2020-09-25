#!/usr/local/bin/python
# coding: latin-1
# Version 5.0

import selenium
import time
import random
import threading
import queue
import subprocess as s

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException
from time import sleep
from difflib import SequenceMatcher
from selenium.webdriver.common.action_chains import ActionChains


class ThreadBetFair(threading.Thread):
	def __init__(self, cola1, cola2, username, password):
		threading.Thread.__init__(self)
		self.cola1 = cola1
		self.cola2 = cola2
		self.username = username
		self.password = password
		self.seguir = True

	def run(self):
		tope_dinero = 20
		# Primer proceso de entrada a la pagina principal
		options = webdriver.ChromeOptions()
		options.add_argument("--start-maximized")
		driver = webdriver.Chrome(chrome_options=options)
		driver.get("https://www.betfair.es")
		# Entrar dentro de la parte de apuestas y cambia idioma
		sportbook = driver.find_element_by_id("SPORTSBOOK")
		sportbook.click()
		sleep(1)
		iniciar_sesion(driver, self.username, self.password)
		sleep(1)
		idioma = driver.find_element_by_xpath("//div[@class='ssc-hls']")
		idioma.click()
		sleep(1)
		ingles = driver.find_element_by_class_name("ssc-GBR")
		ingles.click()
		sleep(1)
		# Entramos en la parte de apuestas en directo
		# Bucle infinito de comprobacion de cotizaciones y partidos
		while(self.seguir == True):
			flag = 0
			directo = driver.find_elements_by_xpath("//li[@class='ui-clickselect']")
			directo[0].click()
			# Entramos en las apuestas en directo de tenis
			sleep(1)
			tenis = driver.find_elements_by_xpath("//span[@class='ip-sport-name']")
			m = 0
			for elemento in tenis:
				m += 1
				if(elemento.text == "Tennis"):
					elemento.click()
					break

			sleep(1)
			#sleep(50000)
			#jugadores = driver.find_elements_by_xpath("(//div[@class='markets-wrapper'])[2]/div[@class='updated-markets']/div/div[@class='sport-2']/ul/li/ul/li/div/div[@class='details-event']/div/a/span[@class='home-team-name']")
			jugadores = driver.find_elements_by_xpath("(//div[@class='markets-wrapper'])[" + str(m) + "]/div[@class='updated-markets']/div/div[@class='sport-2']/ul/li/ul/li/div/div[@class='details-event']/div/a/span[@class='home-team-name']")
			for i in range(len(jugadores)):
				#print("Hola")
				#suspendido = driver.find_elements_by_xpath("((//div[@class='markets-wrapper'])[2]/div[@class='updated-markets']/div/div[@class='sport-2']/ul/li/ul/li/div/div[@class='details-market market-0-runners'])[" + str(i + 1) + "]/div/span")
				suspendido = driver.find_elements_by_xpath("((//div[@class='markets-wrapper'])[" + str(m) + "]/div[@class='updated-markets']/div/div[@class='sport-2']/ul/li/ul/li/div/div[@class='details-market market-0-runners'])[" + str(i + 1) + "]/div/span")
				if suspendido:
					print("Partido suspendido o cerrado")
				else:
					# Chapucilla para arreglar index error, comprobar que ocurre
					try:
						if not jugadores[i].text:
							print("Betfair-> Jugador vacio, seguimos comprobando")
							comprobacion = False
						else:
							self.cola1.put(jugadores[i].text)
							comprobacion = self.cola2.get()
					except IndexError:
						comprobacion = False
	
					if (comprobacion == True):
						# Clickamos y salimos
						#xpath = "((//div[@class='markets-wrapper'])[2]/div[@class='updated-markets']/div/div[@class='sport-2']/ul/li/ul/li/div/div[@class='details-market market-0-runners']/a)[" + str(i + 1) + "]"
						xpath = "((//div[@class='markets-wrapper'])[" + str(m) + "]/div[@class='updated-markets']/div/div[@class='sport-2']/ul/li/ul/li/div/div[@class='details-market market-0-runners']/a)[" + str(i + 1) + "]"
						link = driver.find_element_by_xpath(xpath) # you can use ANY way to locate element
						driver.execute_script("arguments[0].click();", link)
						sleep(1.5)
						# Comenzamos a enviar apuestas al proceso principal desde betfair
						print("Betfair empieza a enviar estadisticas a bet365")
						juego = driver.find_elements_by_xpath("//table[@class='runners-table']/tbody/tr/td")
						# Partido de 3 sets
						#if len(juego) != 13:
							#print("Partido de mas de 3 sets? Numero obtenido-> " + str(len(juego)) + " supuesto jugador-> " + juego[0].text)
						
						#juego = driver.find_elements_by_xpath("//table[@class='runners-table']/tbody/tr/td")
						#print("Recargado numero de juegos-> " + str(len(juego)))

						#print("Partido de 3 sets")
						suma = 0
						set_partido = 1
						juego_actual = 0
						try:
							juego_actual = int(juego[2].text) + int(juego[9].text)
						except:
							juego_actual = 0
						try:
							set2 = int(juego[3].text)
							set_partido += 1
							suma += int(juego[2].text)
							suma += int(juego[9].text)
							juego_actual += int(juego[3].text)
							juego_actual += int(juego[10].text) 
							set3 = int(juego[4].text)
							juego_actual += int(juego[4].text)
							juego_actual += int(juego[11].text)
							set_partido += 1
							suma += set2
							suma += int(juego[10].text)
						except:
							pass
						print("Nos encontramos en el juego " + str(suma) + " del set " + str(set_partido))
						print("El juego actual es: " + str(juego_actual))

						apuestas = driver.find_elements_by_xpath("//div[@class='mod-minimarketview mod-minimarketview-minimarketview yui3-minimarketview-content']")
						j = 0
						while(True):
							try:
								if(j == len(apuestas)):
									break
								comprobacion_apuesta = []
								comprobacion_apuesta.append(False)
								cerrado = driver.find_elements_by_xpath("(//div[@class='mod-minimarketview mod-minimarketview-minimarketview yui3-minimarketview-content'])[" + str(j + 1) + "]/div/div/div[@class='ui-expandable com-expandable-header-anchor']")
								if cerrado:
									driver.execute_script("arguments[0].click();", cerrado[0])

								tipo_apuesta = driver.find_element_by_xpath("(//div[@class='mod-minimarketview mod-minimarketview-minimarketview yui3-minimarketview-content'])[" + str(j + 1) + "]/div/div/div/div/span/span")
								cotizaciones = driver.find_elements_by_xpath("(//div[@class='mod-minimarketview mod-minimarketview-minimarketview yui3-minimarketview-content'])[" + str(j + 1) + "]/div/ul/li/a/span")

								tipo_apuesta_list = tipo_apuesta.text.split()
								print("Betfair, tipo de apuesta antes de comprobar: " + tipo_apuesta.text)
								# Apuesta de tipo ganador del partido
								if(tipo_apuesta_list[1] == "Odds"):
									print("Betfair-> Tipo apuesta: " + tipo_apuesta.text + " Cotizaciones[" + cotizaciones[0].text + "," + cotizaciones[1].text + "]")
									# Margenes para los que bet365 tiene que apostar por encima
									margen = []
									try:
										# Si cambio el porcentaje de beneficio tambien hay que cambiar numeros magicos
										if (float(cotizaciones[0].text) > 1.053):
											margen.append(float(cotizaciones[0].text)/(0.95 * float(cotizaciones[0].text) - 1))
										else:
											margen.append(1000)

										if (float(cotizaciones[1].text) > 1.053):
											margen.append(float(cotizaciones[1].text)/(0.95 * float(cotizaciones[1].text) - 1))
										else:
											margen.append(1000)

										print("Margenes: [" + str(margen[0]) + "," + str(margen[1]) + "]")
									except:
										margen = [1000, 1000]
									self.cola1.put([1, margen[0], margen[1]])
									print("Betfair, enviado tipo apuesta")
									comprobacion_apuesta = self.cola2.get()
								# Apuesta de tipo ganador de juego
								elif(len(tipo_apuesta_list) == 5 and tipo_apuesta_list[0] == "Set" and tipo_apuesta_list[2] == "Game" and tipo_apuesta_list[4] == "Winner"):
									print("Se esta comprobando el juego: " + str(suma + int(tipo_apuesta_list[3])) + " con " + str(juego_actual))
									#if(juego_actual!= 0 and (suma + int(tipo_apuesta_list[3])) != juego_actual + 1):
									print("Betfair-> Tipo apuesta: " + tipo_apuesta.text + " Cotizaciones[" + cotizaciones[0].text + "," + cotizaciones[1].text + "]")
									# Margenes para los que bet365 tiene que apostar por encima
									margen = []
									try:
										# Si cambio el porcentaje de beneficio tambien hay que cambiar numeros magicos
										if (float(cotizaciones[0].text) > 1.053):
											margen.append(float(cotizaciones[0].text)/(0.95 * float(cotizaciones[0].text) - 1))
										else:
											margen.append(1000)

										if (float(cotizaciones[1].text) > 1.053):
											margen.append(float(cotizaciones[1].text)/(0.95 * float(cotizaciones[1].text) - 1))
										else:
											margen.append(1000)

										print("Margenes: [" + str(margen[0]) + "," + str(margen[1]) + "]")
									except:
										margen = [1000, 1000]
									self.cola1.put([8 + suma + int(tipo_apuesta_list[3]), margen[0], margen[1]])
									print("Betfair, enviado tipo apuesta")
									comprobacion_apuesta = self.cola2.get()
								# Apuesta de tipo ganador de set
								elif(len(tipo_apuesta_list) == 3 and tipo_apuesta_list[0] == "Set" and tipo_apuesta_list[2] == "Winner"):
									print("Betfair-> Tipo apuesta: " + tipo_apuesta.text + " Cotizaciones[" + cotizaciones[0].text + "," + cotizaciones[1].text + "]")
									# Margenes para los que bet365 tiene que apostar por encima
									margen = []
									try:
										# Si cambio el porcentaje de beneficio tambien hay que cambiar numeros magicos
										if (float(cotizaciones[0].text) > 1.053):
											margen.append(float(cotizaciones[0].text)/(0.95 * float(cotizaciones[0].text) - 1))
										else:
											margen.append(1000)

										if (float(cotizaciones[1].text) > 1.053):
											margen.append(float(cotizaciones[1].text)/(0.95 * float(cotizaciones[1].text) - 1))
										else:
											margen.append(1000)

										print("Margenes: [" + str(margen[0]) + "," + str(margen[1]) + "]")
									except:
										margen = [1000, 1000]
									# Set de tipo especial en bet365
									if(int(tipo_apuesta_list[1]) == set_partido and int(tipo_apuesta_list[1]) != 3):
										self.cola1.put([2, margen[0], margen[1]])
										print("Betfair, enviado tipo apuesta")
										comprobacion_apuesta = self.cola2.get()
									# Set de tipo normal
									else:
										self.cola1.put([3 + int(tipo_apuesta_list[1]), margen[0], margen[1]])
										print("Betfair, enviado tipo apuesta")
										comprobacion_apuesta = self.cola2.get()

								if(comprobacion_apuesta[0] == True):
									apostar = round(tope_dinero/float(cotizaciones[comprobacion_apuesta[1]].text),2)
									print("SURE BET")
									#print("Betfair, estamos ante una SURE BET-> Cotizacion: " + cotizaciones[comprobacion_apuesta[1]].text + " Dinero a apostar: " + str(20/float(cotizaciones[comprobacion_apuesta[1]].text)) + " Beneficios: 30")
									try:
										driver.execute_script("arguments[0].click();", cotizaciones[comprobacion_apuesta[1]])
										sleep(0.5)
										dinero = driver.find_element_by_class_name("stake")
										dinero.send_keys(str(apostar))
										confirmar = driver.find_element_by_xpath("//button[@class='place-bets-button ui-betslip-action']")
										final = driver.find_element_by_xpath("//div[@class='odds-status ']/span[2]")
										check = self.cola2.get()
										if (check == True):
											if(float(final.text) >= float(cotizaciones[comprobacion_apuesta[1]].text)):
												self.cola1.put(True)
												confirmar.click()
												print("Betfair hace click en apostar")
												s.call(['notify-send','Betfair','Betfair apuesta'])
												sleep(5)
											else:
												print("Betfair no apuesta")
												self.cola1.put(False)
												cancelar = driver.find_element_by_xpath("//a[@class='delete-bet-button ui-betslip-action']")
												cancelar.click()
												s.call(['notify-send','Betfair','Betfair no apuesta por cambio de cotizacion'])
										else:
											print("Betfair no apuesta por culpa de bet")
											self.cola1.put(False)
											cancelar = driver.find_element_by_xpath("//a[@class='delete-bet-button ui-betslip-action']")
											cancelar.click()
											s.call(['notify-send','Betfair','Betfair no apuesta'])
									except Exception as e:
										print("Betfair-> Excepcion: " + str(e))
										self.cola1.put(False)
										cancelar = driver.find_element_by_xpath("//a[@class='delete-bet-button ui-betslip-action']")
										cancelar.click()
										s.call(['notify-send','Betfair','Betfair no apuesta'])
								j += 1

							except:
								apuestas = driver.find_elements_by_xpath("//div[@class='mod-minimarketview mod-minimarketview-minimarketview yui3-minimarketview-content']")
								j += 1

						self.cola1.put([3])
						print("Betfair, enviado fin de apuestas")

						# Volver para seguir comprobando jugadores
						driver.get("https://www.betfair.es/sport/inplay")
						tenis = driver.find_elements_by_xpath("//span[@class='ip-sport-name']")
						for elemento in tenis:
							if(elemento.text == "Tennis"):
								elemento.click()

				jugadores = driver.find_elements_by_xpath("(//div[@class='markets-wrapper'])[2]/div[@class='updated-markets']/div/div[@class='sport-2']/ul/li/ul/li/div/div[@class='details-event']/div/a/span[@class='home-team-name']")


					

	# Funcion que cambia la variable seguir a false y para el hilo
	def parar(self):
		self.seguir = False

# Funcion que devuelve la similitud entre una cadena y otra
def similar(a, b):
	a_aux = a.replace(" (svr)", "").replace(" - servicio", "")
	b_aux = b.replace(" (svr)", "").replace(" - servicio", "")
	a = ngram.NGram.compare(a_aux, b_aux, N=1)
	print("Comparando " + str(a_aux) + " y " + str(b_aux) + " = " + str(a))
	return a

def iniciar_sesion(driverBetFair, username, password):
	usuario = driverBetFair.find_element_by_id("ssc-liu")
	# Introducir el nombre de usuario en lugar de las XXXX
	usuario.send_keys(username)
	contrasenia = driverBetFair.find_element_by_id("ssc-lipw")
	# Introducir la contrasena en lugar de las XXXX
	contrasenia.send_keys(password)
	submit = driverBetFair.find_element_by_id("ssc-lis")
	submit.click()