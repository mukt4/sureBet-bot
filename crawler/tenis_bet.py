#!/usr/local/bin/python
# coding: latin-1
# Version 5.0

import selenium
import time
import random
import threading
import queue
import ngram
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

# Aniadir captura de excepciones en cada try

# Hilo encargado de gestionar las apuestas de bet
class ThreadBet(threading.Thread):
	# Inicializacion del hilo de bet
	def __init__(self, cola1, cola2, username, password):
		# Inicializacion del hilo
		threading.Thread.__init__(self)
		self.cola1 = cola1
		self.cola2 = cola2
		self.username = username
		self.password = password
		self.seguir = True

	def run(self):
		tope_dinero = 20
		options = webdriver.ChromeOptions()
		options.add_argument("--start-maximized")
		driver = webdriver.Chrome(chrome_options=options)
		driver.get("https://www.bet365.es")
		flag_click = 0
		while(flag_click == 0):
			try:
				link = driver.find_element_by_xpath("//ul[@class='lpnm']/li[1]")
				link.click()
				flag_click = 1
			except:
				pass

		sleep(0.5)

		flag_click = 0
		while(flag_click == 0):
			try:
				link = driver.find_element_by_class_name('lpdgl')
				link.click()
				flag_click = 1
			except:
				pass

		sleep(1)
		iniciar_sesion(driver, self.username, self.password)
		# Realizar una espera antes de cada solicitud
		sleep(2)
		# Hay que checkear si cuando termina de revisar apuestas clicka bien en estas vainas
		flag_click = 0
		while(flag_click == 0):
			try:
				link_directo = driver.find_element_by_xpath("//a[@class='hm-BigButton ']")
				link_directo.click()
				flag_click = 1
			except:
				pass

		# Esperas entre solicitudes
		sleep(2)
		# Bucle principal del hilo de bet
		while self.seguir == True:
			flag_click = 0
			while(flag_click == 0):
				try:
					link_generales = driver.find_elements_by_xpath("//div[@class = 'ip-ControlBar_BBarItem ']")
					for link_general in link_generales:
						if(link_general.text == "Overview"):
							link_general.click()
							break
					sleep(2)

					link_deportes = driver.find_elements_by_xpath("//div[@class='ipo-ClassificationBarButtonBase_Label ']")
					for link_deporte in link_deportes:
						if(link_deporte.text == "Tennis"):
							link_deporte.click()
							break
					flag_click = 1
				except:
					inactividad = driver.find_element_by_xpath("//div[@class='wl-InactivityAlert_Remain ']")
					inactividad.click()

			# Realizar una espera antes de cada solicitud
			sleep(1)

			# Una vez el hilo se encuentra en directo y en tenis es necesario que espere a que el hilo de codere le diga
			# en que partido tiene que entrar
			print("Soy bet y estoy esperando que betfair me envie el jugador que tengo que buscar")
			msg_partido = self.cola1.get()
			print("Soy bet y el jugador que he recibido es: " + msg_partido)
			flag = 0

			# Pillamos todos los nombres de los partidos
			link_ligas = driver.find_elements_by_xpath("//div[@class='ipo-Competition ipo-Competition-open ']")

			for i in range(len(link_ligas)):
				xpath = "(//div[@class='ipo-Competition ipo-Competition-open '])[" + str(i + 1) + "]" + "/div[@class='ipo-FixtureRenderer ipo-Competition_Container ']/div[contains(@class,'ipo-Fixture ipo-Fixture_CL13 ipo-Fixture_MainMarkets ') or contains(@class,'ipo-Fixture ipo-Fixture_CL13 ipo-Fixture-hasavicon ipo-Fixture_MainMarkets ')]"
				link_partidos = driver.find_elements_by_xpath(xpath)
				for j in range(len(link_partidos)):
					xpath2 = "(" + xpath + ")[" + str(j + 1) + "]/div/div[@class='ipo-Fixture_ScoreDisplay ipo-ScoreDisplayPoints ']/div/div[@class='ipo-TeamStack ']/div/span[@class='ipo-TeamStack_TeamWrapper ']"
					componentes_partido = driver.find_elements_by_xpath(xpath2)
					flag_check = 0
					for k in range(len(componentes_partido)):
						jugador_bet = componentes_partido[k].text
						print("Comparando " + jugador_bet + " con " + msg_partido)
						# Usar la funcion de comparacion de Paco
						# Comparar nombres separados dentro de la funcion
						if similar(jugador_bet, msg_partido) > 0.8:
							flag = 1
							print("Soy bet, he encontrado el partido y voy a avisar a betfair")
							self.cola2.put(True)
							xpath4 = "(" + xpath + ")[" + str(j + 1) + "]/div/div[@class='ipo-FixtureEventCountButton ']/div[@class='ipo-FixtureEventCountButton_EventCountWrapper ']"
							# Realizar una espera antes de cada solicitud
							flag_click = 0
							while(flag_click == 0):
								try:
									copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath4)))
									driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
									link_bueno = driver.find_element_by_xpath(xpath4)
									link_bueno.click()
									sleep(0.5)
									flag_click = 1
								except:
									pass
							break

					if flag == 1:
						break

				if flag == 1:
					break


			if flag == 0:
				# Mandar senial a bet de que tiene que buscar otro partido
				print("Soy bet365, no he encontrado el partido y voy a avisar a betfair")
				self.cola2.put(False)
			else:
				print("Bet365 empieza a enviar cotizaciones al proceso de estadistica")
				apuestas = driver.find_elements_by_xpath("//div[@class='gl-MarketGroup ']/div/span[@class='gl-MarketGroupButton_Text']")
				# Cambiar esto y hacer diccionario
				dict_apuestas = {}
				for i in range(len(apuestas)):
					try:
						tipo_apuesta = apuestas[i].text.split()
						# print("Apuesta " + str(i + 1) + " del tipo " + str(tipo_apuesta))
						# Ganador de partido y de set especial
						if(len(tipo_apuesta) >= 2 and tipo_apuesta[1] == "Win"):
							xpath = "(//div[@class='gl-MarketGroup '])[" + str(i + 1) + "]/div[@class='gl-MarketGroupButton gl-MarketGroup_HasFavouriteButton ']"
							apertura = driver.find_elements_by_xpath(xpath)
							if apertura:
								driver.execute_script("arguments[0].click();", apertura[0])
								sleep(0.5)
							especifico = driver.find_elements_by_xpath("(//div[@class='gl-MarketGroup '])[" + str(i + 1) + "]/div[@class='gl-MarketGroup_Wrapper ']/div[1]/div/div[contains(@class,'gl-ParticipantOddsOnly gl-Participant_General ipe-CouponParticipantOddsOnlyAdditionalRowHeight ') or contains(@class, 'gl-MarketColumnHeader ')]")
							print("Bet365-> Tipo apuesta(" + apuestas[i].text + "): Cotizaciones[" + especifico[2].text + "," + especifico[3].text + "]")
							dict_apuestas.update({1 : {"cotizaciones" : [float(especifico[2].text), float(especifico[3].text)], "click" : [especifico[2], especifico[3]]}})
							
							if(len(tipo_apuesta) >= 7):
								dict_apuestas.update({2: {"cotizaciones" : [float(especifico[5].text), float(especifico[6].text)], "click" : [especifico[5], especifico[6]]}})

						# Ganador de juego
						elif(len(tipo_apuesta) >=3 and tipo_apuesta[1] == "Game" and tipo_apuesta[2] == "Winner"):
							xpath = "(//div[@class='gl-MarketGroup '])[" + str(i + 1) + "]/div[@class='gl-MarketGroupButton gl-MarketGroup_HasFavouriteButton ']"
							apertura = driver.find_elements_by_xpath(xpath)
							if apertura:
								driver.execute_script("arguments[0].click();", apertura[0])
								sleep(0.5)

							especifico = driver.find_elements_by_xpath("(//div[@class='gl-MarketGroup '])[" + str(i + 1) + "]/div[@class='gl-MarketGroup_Wrapper ']/div/div/div/span")
							# Estamos en el caso de que el jugador esta colocado en el orden bueno
							if (similar2(jugador_bet, especifico[0].text) == 1):
								print("Bet365-> Tipo apuesta(" + apuestas[i].text + ") con colocacion correcta y juego " + tipo_apuesta[0] + " : Cotizaciones[" + especifico[1].text + "," + especifico[3].text + "]")
								dict_apuestas.update({8 + int(tipo_apuesta[0].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")): {"cotizaciones" : [float(especifico[1].text), float(especifico[3].text)], "click" : [especifico[1], especifico[3]]}})
							else:
								print("Bet365-> Tipo apuesta(" + apuestas[i].text + ") con colocacion incorrecta y juego " + tipo_apuesta[0] + " : Cotizaciones[" + especifico[1].text + "," + especifico[3].text + "]")
								dict_apuestas.update({8 + int(tipo_apuesta[0].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")): {"cotizaciones" : [float(especifico[3].text), float(especifico[1].text)], "click" : [especifico[3], especifico[1]]}})

						# Ganador de set normal	
						#elif(len(tipo_apuesta) >=3 and tipo_apuesta[0] == "Set" and tipo_apuesta[2] == "Winner"):
							#xpath = "(//div[@class='gl-MarketGroup '])[" + str(i + 1) + "]/div[@class='gl-MarketGroupButton gl-MarketGroup_HasFavouriteButton ']"
							#apertura = driver.find_elements_by_xpath(xpath)
							#if apertura:
								#driver.execute_script("arguments[0].click();", apertura[0])
								#sleep(0.5)
							
							#especifico = driver.find_elements_by_xpath("(//div[@class='gl-MarketGroup '])[" + str(i + 1) + "]/div[@class='gl-MarketGroup_Wrapper ']/div/div/div/span")
							#print("Bet365-> Tipo apuesta(" + apuestas[i].text + "), set " + tipo_apuesta[1] + " : Cotizaciones[" + especifico[1].text + "," + especifico[3].text + "]")
							#dict_apuestas.update({3 + int(tipo_apuesta[1]): {"cotizaciones" : [float(especifico[1].text), float(especifico[3].text)], "click" : [especifico[1], especifico[3]]}})

					except:
						pass

				print("Bet-> Diccionario de apuestas completo")
				print(str(dict_apuestas))

				apuesta_betfair = self.cola1.get()
				while(apuesta_betfair[0] != 3):
					print("Bet365, recibido tipo apuesta: " + str(apuesta_betfair))
					encontrada = dict_apuestas.get(apuesta_betfair[0])
					if encontrada:
						print("Se ha encontrado apuesta en bet365(" + str(encontrada) + "), comprobamos cotizaciones")
						if(encontrada['cotizaciones'][0] > apuesta_betfair[2]):
							self.cola2.put([True, 1])
							apostar = round(tope_dinero/encontrada['cotizaciones'][0],2)
							print("Bet365, estamos ante una SURE BET-> Cotizacion: " + str(encontrada['cotizaciones'][0]) + " Dinero a apostar: " + str(apostar) + " Beneficios: 30")
							try:
								driver.execute_script("arguments[0].click();",encontrada["click"][0])
								sleep(0.5)
								driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@class='bw-BetslipWebModule_Frame ']"))
								dinero_apostar = driver.find_element_by_xpath("//input[@class='stk bs-Stake_TextBox']")
								dinero_apostar.send_keys(str(apostar))
								try:
									# Apuesta de tipo partido
									if(apuesta_betfair[0] == 1):
										texto_apuesta = driver.find_elements_by_xpath("//div[@class='bs-Selection_Details']")
										if(texto_apuesta[0].text == "Match Winner"):
											self.cola2.put(True)
											comprobacion = self.cola1.get()
										else:
											print("Bet365 no apuesta por no ser ganador del partido")
											self.cola2.put(False)
											descartar = self.cola1.get()
											comprobacion = False
									# Apuesta de tipo ganador de set actual
									elif(apuesta_betfair[0] == 2):
										texto_apuesta = driver.find_elements_by_xpath("//div[@class='bs-Selection_Details']")
										if(texto_apuesta[0].text == "Current Set Winner"):
											self.cola2.put(True)
											comprobacion = self.cola1.get()
										else:
											print("Bet365 no apuesta por no ser set actual")
											self.cola2.put(False)
											descartar = self.cola1.get()
											comprobacion = False
									# Apuesta de tipo ganador de juego
									elif(apuesta_betfair[0] > 8):
										texto_apuesta = driver.find_element_by_xpath("//div[@class='bs-Selection_Desc']")
										texto_apuesta_list = texto_apuesta.text.split()
										if(texto_apuesta_list[-3] == "win" and apuesta_betfair[0] == (8 + int(texto_apuesta_list[-2].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")))):
											self.cola2.put(True)
											comprobacion = self.cola1.get()
										else:
											print(str(texto_apuesta_list))
											print("Bet365 no apuesta por confusion juego 1")
											self.cola2.put(False)
											descartar = self.cola1.get()
											comprobacion = False
									else:
										print("Bet365 no apuesta por confusion juego 2")
										self.cola2.put(False)
										descartar = self.cola1.get()
										comprobacion = False
								except:
									print("Bet365 no apuesta por excepcion")
									self.cola2.put(False)
									descartar = self.cola1.get()
									comprobacion = False

								if comprobacion == True:
									aceptar = driver.find_element_by_xpath("//span[@class='bs-BtnText']")
									aceptar.click()
									s.call(['notify-send','Bet365','Bet365 apuesta'])
									sleep(5)
								else:
									print("Bet365 no apuesta por culpa de betfair")
									s.call(['notify-send','Bet365','Bet365 no apuesta'])
									sleep(5)
									try:
										element = driver.find_element_by_xpath("//div[@class='bs-RemoveColumn']/a")
										driver.execute_script("arguments[0].click();", element)
										flag_click = 1
									except Exception as e:
										print("Bet365-> Excepcion 1: " + str(e))
										print("No se ha podido quitar la cotizacion")
										pass
							except Exception as e:
								print("Bet365-> Excepcion 2: " + str(e))
								self.cola2.put(False)
								descartar = self.cola1.get()
								s.call(['notify-send','Bet365','Bet365 no apuesta'])
								try:
									element = driver.find_element_by_xpath("//div[@class='bs-RemoveColumn']/a")
									driver.execute_script("arguments[0].click();", element)
									flag_click = 1
								except Exception as e:
									print("Bet365-> Excepcion 3: " + str(e))
									print("No se ha podido quitar la cotizacion")
									pass
							driver.switch_to.default_content()
						elif(encontrada['cotizaciones'][1] > apuesta_betfair[1]):
							self.cola2.put([True, 0])
							apostar = round(tope_dinero/encontrada['cotizaciones'][1],2)
							print("Bet365, estamos ante una SURE BET-> Cotizacion: " + str(encontrada['cotizaciones'][1]) + " Dinero a apostar: " + str(apostar) + " Beneficios: 30")
							try:
								driver.execute_script("arguments[0].click();",encontrada["click"][1])
								sleep(0.5)
								driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@class='bw-BetslipWebModule_Frame ']"))
								dinero_apostar = driver.find_element_by_xpath("//input[@class='stk bs-Stake_TextBox']")
								dinero_apostar.send_keys(str(apostar))
								try:
									# Apuesta de tipo partido
									if(apuesta_betfair[0] == 1):
										texto_apuesta = driver.find_elements_by_xpath("//div[@class='bs-Selection_Details']")
										if(texto_apuesta[0].text == "Match Winner"):
											self.cola2.put(True)
											comprobacion = self.cola1.get()
										else:
											print("Bet365 no apuesta por no ser ganador del partido")
											self.cola2.put(False)
											descartar = self.cola1.get()
											comprobacion = False
									# Apuesta de tipo ganador de set actual
									elif(apuesta_betfair[0] == 2):
										texto_apuesta = driver.find_elements_by_xpath("//div[@class='bs-Selection_Details']")
										if(texto_apuesta[0].text == "Current Set Winner"):
											self.cola2.put(True)
											comprobacion = self.cola1.get()
										else:
											print("Bet365 no apuesta por no ser set actual")
											self.cola2.put(False)
											descartar = self.cola1.get()
											comprobacion = False
									# Apuesta de tipo ganador de juego
									elif(apuesta_betfair[0] > 8):
										texto_apuesta = driver.find_element_by_xpath("//div[@class='bs-Selection_Desc']")
										texto_apuesta_list = texto_apuesta.text.split()
										print(str(texto_apuesta_list))
										if(texto_apuesta_list[-3] == "win" and apuesta_betfair[0] == (8 + int(texto_apuesta_list[-2].replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")))):
											self.cola2.put(True)
											comprobacion = self.cola1.get()
										else:
											print("Bet365 no apuesta por confusion juego 1")
											self.cola2.put(False)
											descartar = self.cola1.get()
											comprobacion = False
									else:
										print("Bet365 no apuesta por confusion juego 2")
										self.cola2.put(False)
										descartar = self.cola1.get()
										comprobacion = False
								except:
									print("Bet365 no apuesta por excepcion")
									self.cola2.put(False)
									descartar = self.cola1.get()
									comprobacion = False
									
								if comprobacion == True:
									aceptar = driver.find_element_by_xpath("//span[@class='bs-BtnText']")
									aceptar.click()
									s.call(['notify-send','Bet365','Bet365 apuesta'])
									sleep(5)
								else:
									print("Bet365 no apuesta por culpa de betfair")
									s.call(['notify-send','Bet365','Bet365 no apuesta'])
									try:
										element = driver.find_element_by_xpath("//div[@class='bs-RemoveColumn']/a")
										driver.execute_script("arguments[0].click();", element)
										flag_click = 1
									except Exception as e:
										print("Bet365-> Excepcion 4: " + str(e))
										print("No se ha podido quitar la cotizacion")
										pass

							except Exception as e:
								print("Bet365-> Excepcion 5: " + str(e))
								self.cola2.put(False)
								descartar = self.cola1.get()
								s.call(['notify-send','Bet365','Bet365 no apuesta'])
								try:
									element = driver.find_element_by_xpath("//div[@class='bs-RemoveColumn']/a")
									driver.execute_script("arguments[0].click();", element)
									flag_click = 1
								except Exception as e:
									print("Bet365-> Excepcion 6: " + str(e))
									print("No se ha podido quitar la cotizacion")
									pass

							driver.switch_to.default_content()
						else:
							self.cola2.put([False])
							print("Bet365, no hay sure bet")
					else:
						self.cola2.put([False])
						print("Bet365, no encuentra apuesta")

					print("Obteniendo proxima apuesta")
					apuesta_betfair = self.cola1.get()
	def parar(self):
		self.seguir = False

# Funcion que devuelve la similitud entre una cadena y otra
def similar(a, b):
	print("Similar-> Jugadores recibidos: " + a + " y " + b)
	a_aux = a.replace(" (Svr)", "").replace(" - servicio", "").split("/")
	b_aux = b.replace(" (Svr)", "").replace(" - servicio", "").split("/")
	# Partido de dobles
	if(len(a_aux) == 2):
		if(len(b_aux) == 2):
			print("Partido de dobles")
			a_list = a_aux[0].split()
			a_list2 = a_aux[1].split()
			b_list = b_aux[0].split()
			b_list2 = b_aux[1].split()
			if(len(a_list) > 1 and len(b_list) > 1 and len(a_list2) > 1 and len(b_list2) > 1):
				a = ngram.NGram.compare(a_list[1], b_list[1])
				print("Comparacion " + a_list[1] + " y " + b_list[1] + " -> " + str(a))
				b = ngram.NGram.compare(a_list2[1], b_list2[1])
				print("Comparacion " + a_list2[1] + " y " + b_list2[1] + " -> " + str(b))
			elif(len(b_list) > 1 and len(b_list2) > 1):
				a = ngram.NGram.compare(a_list[0], b_list[1])
				print("Comparacion " + a_list[0] + " y " + b_list[1] + " -> " + str(a))
				b = ngram.NGram.compare(a_list2[0], b_list2[1])
				print("Comparacion " + a_list2[0] + " y " + b_list2[1] + " -> " + str(b))
			else:
				a = ngram.NGram.compare(a_list[0], b_list[0])
				print("Comparacion " + a_list[0] + " y " + b_list[0] + " -> " + str(a))
				b = ngram.NGram.compare(a_list2[0], b_list2[0])
				print("Comparacion " + a_list2[0] + " y " + b_list2[0] + " -> " + str(b))
			if(a > b):
				return a
			else:
				return b
		else:
			print("El segundo jugador no es partido de dobles")
			return 0
	else:
		if(len(b_aux) == 2):
			print("El segundo jugador es partido de dobles")
			return 0
		else:
			print("Partido individual")
			a_list = a_aux[0].split()
			b_list = b_aux[0].split()
			if(len(a_list) > 1 and len(b_list) > 1):
				a = ngram.NGram.compare(a_list[1], b_list[1])
				print("Comparacion " + a_list[1] + " y " + b_list[1] + " -> " + str(a))
			elif(len(b_list) > 1):
				a = ngram.NGram.compare(a_list[0], b_list[1])
				print("Comparacion " + a_list[0] + " y " + b_list[1] + " -> " + str(a))
			elif(len(a_list) > 1):
				a = ngram.NGram.compare(a_list[1], b_list[0])
				print("Comparacion " + a_list[1] + " y " + b_list[0] + " -> " + str(a))
			else:
				a = ngram.NGram.compare(a_list[0], b_list[0])
				print("Comparacion " + a_list[0] + " y " + b_list[0] + " -> " + str(a))
			return a

def similar2(a, b):
	print("Similar2-> Jugadores recibidos " + a + " y " + b)
	a_aux = a.replace(" (Svr)", "")
	b_aux = b.replace(" (Svr)", "")

	print("Comparando " + a_aux + " con " + b_aux)
	if(a_aux == b_aux):
		return 1
	else:
		return 0

def iniciar_sesion(driverBet, username, password):
	flag_click = 0
	while(flag_click == 0):
		try:
			usuario = driverBet.find_element_by_xpath("//div[@class='hm-Login_UserNameWrapper ']/input")
			# Introucir el nombre de usuario en lugar de las XXXX
			usuario.send_keys(username)
			flag_click = 1
		except:
			pass

	flag_click = 0
	sleep(2)
	while(flag_click == 0):
		try:
			contrasenia = driverBet.find_element_by_xpath("//div[@class='hm-Login_PasswordWrapper ']/input[@class='hm-Login_InputField ']")
			contrasenia.send_keys(password)
			flag_click = 1
		except:
			pass

	sleep(1)
	flag_click = 0
	while(flag_click == 0):
		try:
			inicio = driverBet.find_element_by_xpath("//button[@class='hm-Login_LoginBtn ']")
			inicio.click()
			flag_click = 1
		except:
			pass

# Resumen de ids: Ganador del partido: 1, Ganador de juego: 2, Ganador de set especial: 3, Ganador de set normal: 4, Fin de comprobaciones: 5
# Para set sumar 3 y para juego sumar 8