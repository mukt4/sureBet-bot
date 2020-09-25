#!/usr/local/bin/python
# coding: latin-1
# Version 4.0

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

# Pendiente de limpiar bet y optimizar
# Se puede mejorar similar
# Falta hacer apuestas y comprobacion previa de que estan correctas

# Hilo encargado de gestionar las apuestas de bet
class ThreadBet2(threading.Thread):
	# Inicializacion del hilo de bet
	def __init__(self, cola1, cola2, cola3, cola4, username, password):
		# Inicializacion del hilo
		threading.Thread.__init__(self)
		# Cola en la que codere escribe a bet
		self.cola2 = cola2
		# Cola en la que bet escribe al principal
		self.cola3 = cola3
		# Cola en la que bet recibe de principal
		self.cola4 = cola4
		# COla en la que bet escribe a codere
		self.cola1 = cola1
		# Username y password set
		self.username = username
		self.password = password
		# Variable que le dice al hilo si debe contiuar con las apuestas
		self.seguir = True

	def run(self):
		# Variables TESTING
		numero_sure_bet = 0
		options = webdriver.ChromeOptions()
		options.add_argument("--start-maximized")
		driver = webdriver.Chrome(chrome_options=options)
		driver.get("https://www.bet365.es")
		flag_click = 0
		while(flag_click == 0):
			try:
				link = driver.find_element_by_class_name('lpdgl')
				link.click()
				flag_click = 1
			except:
				pass

		iniciar_sesion(driver, self.username, self.password)

		# Realizar una espera antes de cada solicitud
		sleep(2)

		# Hay que checkear si cuando termina de revisar apuestas clicka bien en estas vainas
		flag_click = 0
		while(flag_click == 0):
			try:
				link_directo = driver.find_element_by_xpath("//a[@class='hm-BigButton '][1]")
				link_directo.click()
				flag_click = 1
			except:
				pass

		# Esperas entre solicitudes
		sleep(2)

		# Bucle principal del hilo de bet
		while self.seguir == True:
			flag_click = 0
			while (flag_click == 0):
				try:
					dinero_elemento = driver.find_element_by_xpath("//div[@class='hm-Balance ']")
					dinero_bet = dinero_elemento.text.replace("EUR", "").replace(",",".")
					flag_click = 1
				except:
					pass

			if(float(dinero_bet) < 30):
				print("Bet no dispone de dinero, no se van a realizar apuestas")
				self.seguir = False
			else:
				print("Bet dispone de dinero, se realizan apuestas, dinero bet-> " + dinero_bet)
				flag_click = 0
				while(flag_click == 0):
					try:
						link_generales = driver.find_elements_by_xpath("//div[@class = 'ip-ControlBar_BBarItem ']")
						for link_general in link_generales:
							if(link_general.text == "General"):
								link_general.click()
								break
						sleep(2)

						link_deportes = driver.find_elements_by_xpath("//div[@class='ipo-ClassificationBarButtonBase_Label ']")
						for link_deporte in link_deportes:
							if(link_deporte.text == "Tenis"):
								link_deporte.click()
								break
						flag_click = 1
					except:
						inactividad = driver.find_element_by_xpath("//div[@class='wl-InactivityAlert_Remain ']")
						inactividad.click()

				sleep(1)

				# Una vez el hilo se encuentra en directo y en tenis es necesario que espere a que el hilo de codere le diga
				# en que partido tiene que entrar
				msg_partido = self.cola2.get()
				flag = 0

				# Pillamos todos los nombres de los partidos
				link_ligas = driver.find_elements_by_xpath("//div[@class='ipo-Competition ipo-Competition-open ']")

				for i in range(len(link_ligas)):
					xpath = "(//div[@class='ipo-Competition ipo-Competition-open '])[" + str(i + 1) + "]/div[@class='ipo-FixtureRenderer ipo-Competition_Container ']/div[contains(@class,'ipo-Fixture ipo-Fixture_CL13 ipo-Fixture_MainMarkets ') or contains(@class,'ipo-Fixture ipo-Fixture_CL13 ipo-Fixture-hasavicon ipo-Fixture_MainMarkets ')]"
					link_partidos = driver.find_elements_by_xpath(xpath)
					for j in range(len(link_partidos)):
						xpath2 = "(" + xpath + ")[" + str(j + 1) + "]/div/div[@class='ipo-Fixture_ScoreDisplay ipo-ScoreDisplayPoints ']/div/div[@class='ipo-TeamStack ']/div/span[@class='ipo-TeamStack_TeamWrapper ']"
						componentes_partido = driver.find_elements_by_xpath(xpath2)
						flag_check = 0
						for k in range(len(componentes_partido)):

							if similar(componentes_partido[k].text.lower(), msg_partido.decode("utf-8", "latin-1")) > 0.7:
								flag = 1
								# Esta flag se pone a 1 para comprobar si el jugador que se ha encontrado esta en el orden correcto
								if k == 1:
									flag_check = 1

								self.cola1.put(True)
								xpath4 = "(//div[@class='ipo-Competition ipo-Competition-open '])[" + str(i + 1) + "]/div[@class='ipo-FixtureRenderer ipo-Competition_Container ']/div[" + str(j + 1) + "]/div/div[@class='ipo-FixtureEventCountButton ']/div[@class='ipo-FixtureEventCountButton_EventCountWrapper ']"
								# Realizar una espera antes de cada solicitud
								flag_click = 0
								while(flag_click == 0):
									try:
										copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath4)))
										driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
										link_bueno = driver.find_element_by_xpath(xpath4)
										link_bueno.click()
										flag_click = 1
									except:
										inactividad = driver.find_elements_by_xpath("//div[@class='wl-InactivityAlert_Remain ']")
										if(len(inactividad) == 1):
											inactividad.click()
										pass
								break

						if flag == 1:
							break

					if flag == 1:
						break


				if flag == 0:
					# Mandar senial a bet de que tiene que buscar otro partido
					self.cola1.put(False)
				else:
					# Bucle infinito hasta que codere nos diga que hemos cambiado de jugador
					while(True):
						# Volvemos a poner la flag a 0 para analizar el tipo de apuesta
						flag = 0
						# Ya nos encontramos en el partido esperado
						sleep(2)
						apuestas = driver.find_elements_by_xpath("//div[@class='gl-MarketGroup ']")
						tipo_apuesta = self.cola2.get()
						print("BET->Tipo apuestar recibida: " + str(tipo_apuesta))

						# Comprobamos en bucle si existe la apuesta deseada
						if(tipo_apuesta[0] == "Continuar"):
							self.cola1.put(True)
							break
						else:
							if (tipo_apuesta[0] == "Ganara"):
								apuesta_bet = bytes("Ganar\xc3\xa1", "latin-1")
							#elif (tipo_apuesta[0] == "Encuentro"):
								#apuesta_bet = bytes("Encuentro - H\xc3\xa1ndicap", "latin-1")
							elif (tipo_apuesta[0] == "Set"):
								if(tipo_apuesta[2] == True):
									apuesta_bet = bytes("Ganar\xc3\xa1", "latin-1")
								else:
									apuesta_bet = bytes(str(tipo_apuesta[1]) + "\xc2\xba Set - Ganador")
							#elif(tipo_apuesta[0] == "Punto"):
								#apuesta_bet = bytes("Apuestas al punto - " + str(int(float(tipo_apuesta[1]))) + "\xc2\xba juego", "latin-1")
							elif(tipo_apuesta[0] == "Juego"):
								apuesta_bet = bytes("Ganador del " + str(int(float(tipo_apuesta[1]))) + "\xc2\xba juego", "latin-1")

							for i in range(len(apuestas)):
								# Checkear si en todos los casos se cumplde div[1]
								xpath = "(//div[@class='gl-MarketGroup '])[" + str(i + 1) + "]/div[1]/span"
								try:
									apuesta = driver.find_element_by_xpath(xpath).text
								except:
									break
								
								print("BET->Analizando apuesta: " + str(apuesta))
								print("BET->Comparando " + str(apuesta.encode("utf-8")) + " con " + str(apuesta_bet))
								if (apuesta.encode("utf-8") == apuesta_bet):
									print("Apuesta encontrada")
									xpath2 = "(//div[@class='gl-MarketGroup '])[" + str(i + 1) + "]/div[@class='gl-MarketGroupButton gl-MarketGroup_HasFavouriteButton ']"
									link_apuesta = driver.find_elements_by_xpath(xpath2)
									# Si estamos en este caso hay que abrir la apuesta
									flag_click = 0
									while(flag_click == 0):
										try:
											if (link_apuesta):
												copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath2)))
												driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
												abrir = driver.find_element_by_xpath(xpath2)
												abrir.click()
												flag_click = 1
											else:
												flag_click = 1
										except:
											inactividad = driver.find_elements_by_xpath("//div[@class='wl-InactivityAlert_Remain ']")
											if(len(inactividad) == 1):
												inactividad.click()
											pass

									# Si la apuesta ya esta abierta
									if (tipo_apuesta[0] == "Ganara"):
										self.cola1.put(True)
										# print("Bet(Tipo apuesta)-> " + apuesta.encode("utf-8", "latin-1"))
										flag = 1
										xpath2 = "(//div[@class='gl-MarketGroup '])["+ str(i + 1) + "]/div[@class='gl-MarketGroup_Wrapper ']/div/div[1]/div[@class='gl-ParticipantRowName '][1]/span"
										jugador = driver.find_element_by_xpath(xpath2).text.lower()
										if(similar(jugador, str(msg_partido.decode("utf-8", "latin-1"))) > 0.7):
											flag_check = 0
										else:
											flag_check = 1
										xpath2 = "(//div[@class='gl-MarketGroup '])["+ str(i + 1) + "]/div[@class='gl-MarketGroup_Wrapper ']/div/div[2]/div[@class='gl-ParticipantOddsOnly gl-Participant_General ipe-CouponParticipantOddsOnlyAdditionalRowHeight ']/span"
										try:
											cotizaciones_aux = driver.find_elements_by_xpath(xpath2)
											cotizaciones = [cotizaciones_aux[0].text, cotizaciones_aux[1].text]
											if flag_check == 0:
												self.cola3.put([cotizaciones[0], cotizaciones[1]])
											else:
												self.cola3.put([cotizaciones[1], cotizaciones[0]])
										except:
											self.cola3.put(["0.1", "0.1"])
											break

										break
									# AQUI IRIA HANDICAP
									# Nos encontramos ante una apuesta de tipo ganador de set/juego/punto
									elif (tipo_apuesta[0] == "Set"):
										flag = 1
										self.cola1.put(True)
										# Si nos encontramos en el set actual
										if (tipo_apuesta[2] ==  True):
											xpath2 = "(//div[@class='gl-MarketGroup '])["+ str(i + 1) + "]/div[@class='gl-MarketGroup_Wrapper ']/div/div[1]/div[@class='gl-ParticipantRowName '][1]/span"
											try:
												jugador = driver.find_element_by_xpath(xpath2).text.lower()
											except:
												self.cola3.put(["0.1", "0.1"])
												break
											if(similar(jugador, str(msg_partido.decode("utf-8", "latin-1"))) > 0.7):
												flag_check = 0
											else:
												flag_check = 1
											xpath2 = "(//div[@class='gl-MarketGroup '])["+ str(i + 1) + "]/div[@class='gl-MarketGroup_Wrapper ']/div/div[3]/div[@class='gl-ParticipantOddsOnly gl-Participant_General ipe-CouponParticipantOddsOnlyAdditionalRowHeight ']/span"
											try:
												cotizaciones_aux = driver.find_elements_by_xpath(xpath2)
												cotizaciones = [cotizaciones_aux[0].text, cotizaciones_aux[1].text]
											except:
												cotizaciones = ["0.1", "0.1"]
										else:
											xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div/div[1]/span[@class='gl-Participant_Name']"
											try:
												jugador = driver.find_element_by_xpath(xpath2).text.lower()
											except:
												self.cola3.put(["0.1", "0.1"])
												break
											if(similar(jugador, str(msg_partido.decode("utf-8", "latin-1"))) > 0.7):
												flag_check = 0
											else:
												flag_check = 1
											xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div/div/span[contains(@class,'gl-ParticipantCentered_Odds') or contains(@class,'gl-Participant_Odds')]"
											try:
												cotizaciones_aux = driver.find_elements_by_xpath(xpath2)
												cotizaciones = [cotizaciones_aux[0].text, cotizaciones_aux[1].text]
											except:
												cotizaciones = ["0.1", "0.1"]
										try:
											if flag_check == 0:
												self.cola3.put([cotizaciones[0], cotizaciones[1]])
											else:
												self.cola3.put([cotizaciones[1], cotizaciones[0]])
										except:
											self.cola3.put(["0.1", "0.1"])
										break
									# Xpath correcto
									elif (tipo_apuesta[0] == "Juego"):
										flag = 1
										self.cola1.put(True)
										# print("Bet(Tipo apuesta)-> " + apuesta.encode("utf-8", "latin-1"))
										xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div/div[1]/span[@class='gl-Participant_Name']"
										try:
											jugador = driver.find_element_by_xpath(xpath2).text.lower()
										except:
											self.cola3.put(["0.1", "0.1"])
											break
										if(similar(jugador, str(msg_partido.decode("utf-8", "latin-1"))) > 0.7):
											flag_check = 0
										else:
											flag_check = 1
										xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div/div/span[contains(@class,'gl-ParticipantCentered_Odds') or contains(@class,'gl-Participant_Odds')]"
										cotizaciones_aux = driver.find_elements_by_xpath(xpath2)
										try:
											cotizaciones = [cotizaciones_aux[0].text, cotizaciones_aux[1].text]
											if flag_check == 0:
												self.cola3.put([cotizaciones[0], cotizaciones[1]])
											else:
												self.cola3.put([cotizaciones[1], cotizaciones[0]])
										except:
											self.cola3.put(["0.1", "0.1"])

										break
									# Aqui iria apuestas al punto, que esta abajo

							# Esperamos a que el proceos principal nos confirme si estamos ante una sure bet
							if flag == 1:
								datos = self.cola4.get()
								# Si estamos ante sure bet hacemos las apuestas necesarias
								if datos[0] == True:
									apuesta1 = datos[1]
									apuesta2 = datos[2]
									try:
										# Si el importe por la primera apuesta es 0, significa que hay que apostar al segundo
										apuesta = driver.find_elements_by_xpath(xpath2)
										print("Realizando comprobaciones")
										if apuesta1 == 0:
											print("Hay que apostar por el segundo jugador")
											# Comprobamos si el orden es el bueno
											if flag_check == 0:
												try:
													apuesta[1].click()
												except:
													inactividad = driver.find_elements_by_xpath("//div[@class='wl-InactivityAlert_Remain ']")
													if(len(inactividad) == 1):
														inactividad.click()
												sleep(0.5)
												# Nos cambiamos a realizar comprobaciones sobre el frame
												driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@class='bw-BetslipWebModule_Frame ']"))
												flag_click = 0
												while(flag_click == 0):
													try:
														jugador_apuesta = driver.find_element_by_xpath("//div[@class='bs-Selection']/div[@class='bs-Selection_Desc']")
														flag_click = 1
													except:
														pass
												jugador_apuesta_lista = jugador_apuesta.text.split(" - ")
												# Comprobamos el jugador
												print("Bet se encuentra en el caso de apostar por el segundo jugador con el orden correcto")
												print("Bet apostando-> Comparando " + str(jugador_apuesta_lista[0].lower()) + " con " + str(msg_partido.decode("utf-8", "latin-1")))
												if(similar(jugador_apuesta_lista[0].lower(), msg_partido.decode("utf-8", "latin-1")) < 0.7):
													todo_correcto = True
													print("Bet-> Se ha comprobado el jugador correctamente")
												else:
													todo_correcto = False
													print("Bet-> Error comprobando el jugador")

												# Comprobar tipo apuesta
												if(len(jugador_apuesta_lista) == 1):
													# Estamos ante una apuesta de ganador del partido
													if(tipo_apuesta[0] != "Ganara"):
														todo_correcto = False
														print("Bet-> Error comprobando la apuesta")
													else:
														print("Bet-> Se ha comprobado la apuesta correctamente")
												else:
													# Estamos ante una apuesta de ganador de set o ganador de juego
													if (tipo_apuesta[0] == "Set"):
														comparar = bytes("Ganar\xc3\xa1 el " + str(tipo_apuesta[1]) + "\xc2\xba set", "latin-1")
													elif(tipo_apuesta[0] == "Juego"):
														comparar = bytes("Ganar\xc3\xa1 el " + str(int(float(tipo_apuesta[1]))) + "\xc2\xba juego", "latin-1")
													else:
														comparar = "Valor por defecto"

													print("Bet apostando-> Comparando " + str(jugador_apuesta_lista[1].encode("utf-8", "latin-1")) + " con " + str(comparar))

													if(comparar == jugador_apuesta_lista[1].encode("utf-8", "latin-1")):
														print("Bet-> Se ha comprobado el tipo de apuesta correctamente")
													else:
														print("Bet-> Error comprobando la apuesta")
														todo_correcto = False

												flag_click = 0
												while(flag_click == 0):
													try:
														cotizacion_apuesta = driver.find_element_by_xpath("//div[@class='bs-Odds']")
														print("Bet-> Comparando cotizaciones " + str(cotizacion_apuesta.text) + " con " + str(cotizaciones[1]))
														try:
															if(float(cotizacion_apuesta.text) >= float(cotizaciones[1])):
																print("Bet-> Se ha comprobado la cotizacion correctamente")	
															else:
																print("Bet-> Error en la cotizacion")
																todo_correcto = False
														except:
															todo_correcto = False
														flag_click = 1
													except:
														pass
											else:
												apuesta[0].click()
												sleep(0.5)
												# Nos cambiamos a realizar comprobaciones sobre el frame
												driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@class='bw-BetslipWebModule_Frame ']"))
												flag_click = 0
												while(flag_click == 0):
													try:
														jugador_apuesta = driver.find_element_by_xpath("//div[@class='bs-Selection']/div[@class='bs-Selection_Desc']")
														flag_click = 1
													except:
														pass
												jugador_apuesta_lista = jugador_apuesta.text.split(" - ")
												# Comprobamos el jugador
												print("Bet se encuentra en el caso de apostar por el segundo jugador con el orden incorrecto")
												print("Bet apostando-> Comparando " + str(jugador_apuesta_lista[0].lower()) + " con " + str(msg_partido.decode("utf-8", "latin-1")))
												if(similar(jugador_apuesta_lista[0].lower(), msg_partido.decode("utf-8", "latin-1")) < 0.7):
													todo_correcto = True
													print("Bet-> Se ha comprobado el jugador correctamente")
												else:
													todo_correcto = False
													print("Bet-> Error comprobando el jugador")

												# Comprobar tipo apuesta
												if(len(jugador_apuesta_lista) == 1):
													# Estamos ante una apuesta de ganador del partido
													if(tipo_apuesta[0] != "Ganara"):
														todo_correcto = False
														print("Bet-> Error comprobando la apuesta")
													else:
														print("Bet-> Se ha comprobado la apuesta correctamente")
												else:
													# Estamos ante una apuesta de ganador de set o ganador de juego
													if (tipo_apuesta[0] == "Set"):
														comparar = bytes("Ganar\xc3\xa1 el " + str(tipo_apuesta[1]) + "\xc2\xba set", "latin-1")
													elif(tipo_apuesta[0] == "Juego"):
														comparar = bytes("Ganar\xc3\xa1 el " + str(int(float(tipo_apuesta[1]))) + "\xc2\xba juego", "latin-1")
													else:
														comparar = "Valor por defecto"

													print("Bet apostando-> Comparando " + str(jugador_apuesta_lista[1].encode("utf-8", "latin-1")) + " con " + str(comparar))

													if(comparar == jugador_apuesta_lista[1].encode("utf-8", "latin-1")):
														print("Bet-> Se ha comprobado el tipo de apuesta correctamente")
													else:
														print("Bet-> Error comprobando la apuesta")
														todo_correcto = False

												flag_click = 0
												while(flag_click == 0):
													try:
														cotizacion_apuesta = driver.find_element_by_xpath("//div[@class='bs-Odds']")
														print("Bet-> Comparando cotizaciones " + str(cotizacion_apuesta.text) + " con " + str(cotizaciones[1]))
														try:
															if(float(cotizacion_apuesta.text) >= float(cotizaciones[0])):
																print("Bet-> Se ha comprobado la cotizacion correctamente")	
															else:
																print("Bet-> Error en la cotizacion")
																todo_correcto = False
														except:
															todo_correcto = False
														flag_click = 1
													except:
														pass

										# Apuestas en las que hay que apostar por el primer jugador
										else:
											print("Hay que apostar por el primer jugador")
											if flag_check == 0:
												try:
													apuesta[0].click()
												except:
													inactividad = driver.find_elements_by_xpath("//div[@class='wl-InactivityAlert_Remain ']")
													if(len(inactividad) == 1):
														inactividad.click()
												# Nos cambiamos a realizar comprobaciones sobre el frame
												driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@class='bw-BetslipWebModule_Frame ']"))
												sleep(0.5)
												flag_click = 0
												while(flag_click == 0):
													try:
														jugador_apuesta = driver.find_element_by_xpath("//div[@class='bs-Selection']/div[@class='bs-Selection_Desc']")
														flag_click = 1
													except:
														pass
												jugador_apuesta_lista = jugador_apuesta.text.split(" - ")
												# Comprobamos el jugador
												print("Bet se encuentra en el caso de apostar por el primer jugador con el orden correcto")
												print("Bet apostando-> Comparando " + str(jugador_apuesta_lista[0].lower()) + " con " + str(msg_partido.decode("utf-8", "latin-1")))
												if(similar(jugador_apuesta_lista[0].lower(), msg_partido.decode("utf-8", "latin-1")) > 0.7):
													todo_correcto = True
													print("Bet-> Se ha comprobado el jugador correctamente")
												else:
													todo_correcto = False
													print("Bet-> Error comprobando el jugador")

												# Comprobar tipo apuesta
												if(len(jugador_apuesta_lista) == 1):
													# Estamos ante una apuesta de ganador del partido
													if(tipo_apuesta[0] != "Ganara"):
														todo_correcto = False
														print("Bet-> Error comprobando la apuesta")
													else:
														print("Bet-> Se ha comprobado la apuesta correctamente")
												else:
													# Estamos ante una apuesta de ganador de set o ganador de juego
													if (tipo_apuesta[0] == "Set"):
														comparar = bytes("Ganar\xc3\xa1 el " + str(tipo_apuesta[1]) + "\xc2\xba set", "latin-1")
													elif(tipo_apuesta[0] == "Juego"):
														comparar = bytes("Ganar\xc3\xa1 el " + str(int(float(tipo_apuesta[1]))) + "\xc2\xba juego", "latin-1")
													else:
														comparar = "Valor por defecto"

													print("Bet apostando-> Comparando " + str(jugador_apuesta_lista[1].encode("utf-8")) + " con " + str(comparar))
													if(comparar == jugador_apuesta_lista[1].encode("utf-8", "latin-1")):
														print("Bet-> Se ha comprobado el tipo de apuesta correctamente")
													else:
														print("Bet-> Error comprobando la apuesta")
														todo_correcto = False

												flag_click = 0
												while(flag_click == 0):
													try:
														cotizacion_apuesta = driver.find_element_by_xpath("//div[@class='bs-Odds']")
														print("Bet-> Comparando cotizaciones " + str(cotizacion_apuesta.text) + " con " + str(cotizaciones[0]))
														try:
															if(float(cotizacion_apuesta.text) >= float(cotizaciones[0])):
																print("Bet-> Se ha comprobado la cotizacion correctamente")	
															else:
																print("Bet-> Error en la cotizacion")
																todo_correcto = False
														except:
															todo_correcto = False
														flag_click = 1
													except:
														pass
											else:
												try:
													apuesta[1].click()
												except:
													inactividad = driver.find_elements_by_xpath("//div[@class='wl-InactivityAlert_Remain ']")
													if(len(inactividad) == 1):
														inactividad.click()
												sleep(0.5)
												# Nos cambiamos a realizar comprobaciones sobre el frame
												driver.switch_to_frame(driver.find_element_by_xpath("//iframe[@class='bw-BetslipWebModule_Frame ']"))
												flag_click = 0
												while(flag_click == 0):
													try:
														jugador_apuesta = driver.find_element_by_xpath("//div[@class='bs-Selection']/div[@class='bs-Selection_Desc']")
														flag_click = 1
													except:
														pass
												jugador_apuesta_lista = jugador_apuesta.text.split(" - ")
												# Comprobamos el jugador
												print("Bet se encuentra en el caso de apostar por el primer jugador con el orden incorrecto")
												print("Bet apostando-> Comparando " + str(jugador_apuesta_lista[0].lower()) + " con " + str(msg_partido.decode("utf-8", "latin-1")))
												if(similar(jugador_apuesta_lista[0].lower(), msg_partido.decode("utf-8", "latin-1")) > 0.7):
													todo_correcto = True
													print("Bet-> Se ha comprobado el jugador correctamente")
												else:
													todo_correcto = False
													print("Bet-> Error comprobando el jugador")

												# Comprobar tipo apuesta
												if(len(jugador_apuesta_lista) == 1):
													# Estamos ante una apuesta de ganador del partido
													if(tipo_apuesta[0] != "Ganara"):
														todo_correcto = False
														print("Bet-> Error comprobando la apuesta")
													else:
														print("Bet-> Se ha comprobado la apuesta correctamente")
												else:
													# Estamos ante una apuesta de ganador de set o ganador de juego
													if (tipo_apuesta[0] == "Set"):
														comparar = bytes("Ganar\xc3\xa1 el " + str(tipo_apuesta[1]) + "\xc2\xba set", "latin-1")
													elif(tipo_apuesta[0] == "Juego"):
														comparar = bytes("Ganar\xc3\xa1 el " + str(int(float(tipo_apuesta[1]))) + "\xc2\xba juego", "latin-1")
													else:
														comparar = "Valor por defecto"

													print("Bet apostando-> Comparando " + str(jugador_apuesta_lista[1].encode("utf-8")) + " con " + str(comparar))
													if(comparar == jugador_apuesta_lista[1].encode("utf-8", "latin-1")):
														print("Bet-> Se ha comprobado el tipo de apuesta correctamente")
													else:
														print("Bet-> Error comprobando la apuesta")
														todo_correcto = False

												flag_click = 0
												while(flag_click == 0):
													try:
														cotizacion_apuesta = driver.find_element_by_xpath("//div[@class='bs-Odds']")
														print("Bet-> Comparando cotizaciones " + str(cotizacion_apuesta.text) + " con " + str(cotizaciones[1]))
														try:
															if(float(cotizacion_apuesta.text) >= float(cotizaciones[1])):
																print("Bet-> Se ha comprobado la cotizacion correctamente")	
															else:
																print("Bet-> Error en la cotizacion")
																todo_correcto = False
														except:
															todo_correcto = False
														flag_click = 1
													except:
														pass

										if todo_correcto == True:
											# Aqui se realizaria la pauesta, en vez de eso voy a comprobar que esta correcto
											try:
												dinero = driver.find_element_by_xpath("//input[@class='stk bs-Stake_TextBox']")
												if apuesta1 == 0:
													dinero.send_keys(str(apuesta2))
													print("Soy bet y voy a apostar " + str(apuesta2))
												else:
													dinero.send_keys(str(apuesta1))
													print("Soy bet y voy a apostar " + str(apuesta1))
												self.cola1.put(True)
												comprobacion = self.cola2.get()
												if comprobacion == True:
													print("Soy bet y me ha confirmado codere asi que voy a realizar apuesta")
													s.call(['notify-send','Bet','Sure bet encontrada'])
													flag_click = 0
													while(flag_click == 0):
														try:
															aceptar = driver.find_element_by_xpath("//span[@class='bs-BtnText']")
															aceptar.click()
															flag_click = 1
															print("Bet-> Se ha realizado la apuesta")

														except Exception as e:
															print("Error al apostar bet-> " + str(e))
															flag_click = 1
															print("Bet-> No se ha realizado la apuesta")
															pass 
													driver.switch_to.default_content()
												else:
													print("Codere me ha avisado que no hay que realizar apuesta")
													flag_click = 0
													while(flag_click == 0):
														try:
															element = driver.find_element_by_xpath("//div[@class='bs-RemoveColumn']/a")
															driver.execute_script("arguments[0].click();", element)
															flag_click = 1
														except:
															print("No se ha podido quitar la cotizacion")
															pass
													print("Se ha quitado la apuesta correctamente")
													driver.switch_to.default_content()
												#Cancelamos la apuesta y continuamos
											except:
												print("Ha pasado algo a la hora de introducir el dinero de la apuesta")
												# Avisariamos a codere de que ha habido un error
												self.cola1.put(False)
												# Descartamos su comprobacion
												comprobacion = self.cola2.get()
												flag_click = 0
												while(flag_click == 0):
													try:
														element = driver.find_element_by_xpath("//div[@class='bs-RemoveColumn']/a")
														driver.execute_script("arguments[0].click();", element)
														flag_click = 1
													except:
														print("No se ha podido quitar la cotizacion")
														pass
												print("Se ha quitado la apuesta correctamente")
												driver.switch_to.default_content()
												pass

										else:
											# Hay que avisar a codere de que no haga apuesta
											####################################
											self.cola1.put(False)
											comprobacion = self.cola2.get()
											####################################
											# Desechamos la comprobacion y seguimos comprobando sure bet
											print("Apuesta incorrecta")

											# Quitamos tambien la apuesta de bet
											flag_click = 0
											while(flag_click == 0):
												try:
													element = driver.find_element_by_xpath("//div[@class='bs-RemoveColumn']/a")
													driver.execute_script("arguments[0].click();", element)
													flag_click = 1
												except:
													print("No se ha podido quitar la cotizacion")
													pass
											print("Se ha quitado la apuesta correctamente")
											driver.switch_to.default_content()


									# Si se produce algun error no se hace la apuesta
									except Exception as e:
										print("Se ha producido un error, asi que no se realiza apuesta")
										print("El error es el siguiente " + str(e))
										flag_click = 0
										contador = 0
										while(flag_click == 0):
											try:
												contador += 1
												element = driver.find_element_by_xpath("//div[@class='bs-RemoveColumn']/a")
												driver.execute_script("arguments[0].click();", element)
												flag_click = 1
											except:
												if contador == 15:
													flag_click = 1
												pass
										driver.switch_to.default_content()
										# Hay que avisar a codere de que no haga apuesta
										self.cola1.put(False)
										# Descartamos lo que nos dice codere
										descartar = self.cola2.get()

							# Comprobamos si el tipo de apuesta es continuar para seguir buscando en otros jugadores
							else:
								self.cola1.put(False)

	# Funcion que cambia la variable seguir a false y para el hilo
	def parar(self):
		self.seguir = False

# Funcion que devuelve la similitud entre una cadena y otra
# Fcking python3 hay que repasar esta mierda
def similar(a, b):
	a_aux = a.replace(" (svr)", "").replace(" - servicio", "")
	b_aux = b.replace(" (svr)", "").replace(" - servicio", "")
	a = ngram.NGram.compare(a_aux, b_aux, N=1)
	print("Comparando " + str(a_aux) + " y " + str(b_aux) + " = " + str(a))
	return a

def iniciar_sesion(driverBet, username, password):
	flag_click = 0
	while(flag_click == 0):
		try:
			usuario = driverBet.find_element_by_xpath("//div[@class='hm-Login_UserNameWrapper ']/input")
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

####################################
# Apuestas al punto
def punto():
	if (tipo_apuesta[0] == "Punto"):
		xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div[1]/div/span"
		# print("Bet-> Comprobando apuesta al punto")
		puntos = driver.find_elements_by_xpath(xpath2)
		# Guardamos el punto en el que nos encontramos para hacer el xpath bueno
		punto_aux = 100
		for ii in range(len(puntos)):
			try:
				if (puntos[ii].text == tipo_apuesta[2]):
					punto_aux = ii
			except:
				break
		if (punto_aux == 100):
			flag = 0
			#break
		else:
			flag = 1
			self.cola1.put(True)
			#print("Bet(Tipo apuesta)-> " + apuesta.encode("utf-8", "latin-1"))
			xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div[2]/div[1]"
			try:
				jugador = driver.find_element_by_xpath(xpath2).text.lower()
			except:
				self.cola3.put(["0.1", "0.1"])
				#break
			if(similar(jugador, str(msg_partido.decode("utf-8", "latin-1"))) > 0.7):
				flag_check = 0
			else:
				flag_check = 1
			xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div[position() = 2 or position() = 3]/div[" + str(punto_aux + 2) + "]/span[@class='gl-ParticipantCentered_Odds']"
			cotizaciones = driver.find_elements_by_xpath(xpath2)
			try:
				if flag_check == 0:
					self.cola3.put([cotizaciones[0].text, cotizaciones[1].text])
				else:
					self.cola3.put([cotizaciones[1].text, cotizaciones[0].text])
			except:
				self.cola3.put(["0.1", "0.1"])
			#try:
				#print("Bet(cotizaciones)-> [" + cotizaciones[0].text + "," + cotizaciones[1].text + "]")
			#except:
				#print("Bet(cotizaciones)-> [x,y]") 
			#break

	#APUESTA TIPO HANDICAP
	elif (tipo_apuesta[0] == "Encuentro"):
		self.cola1.put(True)
		# print("Bet(Tipo apuesta)-> " + apuesta.encode("utf-8", "latin-1"))
		flag = 1
		xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div/div[1]/span[@class='gl-Participant_Name']"
		try:
			jugador = driver.find_element_by_xpath(xpath2).text.lower()
		except:
			self.cola3.put(["0.1", "0.1"])
			#break
		if(similar(jugador, str(msg_partido.decode("utf-8", "latin-1"))) > 0.7):
			flag_check = 0
		else:
			flag_check = 1
		xpath2 = "//div[@class='gl-MarketGroup '][" + str(i + 1) + "]/div[2]/div/div/div/span[contains(@class,'gl-ParticipantCentered_Odds') or contains(@class,'gl-Participant_Odds')]"
		try:
			cotizaciones = driver.find_elements_by_xpath(xpath2)
			if flag_check == 0:
				self.cola3.put([cotizaciones[0].text, cotizaciones[1].text])
			else:
				self.cola3.put([cotizaciones[1].text, cotizaciones[0].text])
		except:
			self.cola3.put(["0.1", "0.1"])
		#try:
			# print("Bet(cotizaciones)-> [" + cotizaciones[0].text + "," + cotizaciones[1].text + "]")
		#except:
			#print("Bet(cotizaciones)-> [x,y]") 
		#break
