#!/usr/local/bin/python
# coding: latin-1
# Version 4.0

import time
import queue
import threading
import selenium
import random
import threading
import ngram
import subprocess as s

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
from difflib import SequenceMatcher
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException
from selenium.webdriver.common.action_chains import ActionChains

# Codere limpio y finiquitado
# Se puede tratar de mejorar similar

class ThreadCodere(threading.Thread):
	
	# Inicializacion del hilo de bet
	def __init__(self, cola1, cola2, cola5, cola6, username, password):
		# Inicializacion del hilo
		threading.Thread.__init__(self)
		# Cola en la que codere escribe a bet
		self.cola2 = cola2
		# Cola en la que codere escribe al principal
		self.cola5 = cola5
		# Cola en la que codere recibe de principal
		self.cola6 = cola6
		# Cola en la que bet escribe a codere
		self.cola1 = cola1
		# Set username and password
		self.username = username
		self.password = password
		# Variable que le dice al hilo si debe contiuar con las apuestas
		self.seguir = True

	# //button[@class='alert-button alert-button-md alert-button-default alert-button-default-md']

	def run(self):
		# Variables TESTING
		numero_sure_bet = 0

		# Hay que inciar sesion en codere
		options = webdriver.ChromeOptions()
		options.add_argument("--start-maximized")
		driver = webdriver.Chrome(chrome_options=options)
		driver.get("https://www.codere.es/inicio")
		flag_click = 0

		sleep(2)
		iniciar_sesion(driver, self.username, self.password)
		sleep(3)
		flag_click = 0
		while(flag_click == 0):
			try:
				aceptar = driver.find_element_by_xpath("//button[@class='alert-button alert-button-md alert-button-default alert-button-default-md']")
				aceptar.click()
				flag_click = 1
			except:
				pass

		sleep(2)
		flag_click = 0
		while(flag_click == 0):
			try:
				link = driver.find_element_by_xpath("(//button[@class='nav-item bar-button bar-button-md bar-button-default bar-button-default-md'])[1]")
				link.click()
				flag_click = 1
			except:
				print("POSIBLE FIN DE TENIS")
				pass

		# Realizar una espera antes de cada solicitud
		sleep(4)

		#Boton cookies
		#flag_click = 0
		#while(flag_click == 0):
			#try:
				#boton = driver.find_element_by_xpath("//button[@class='alert-button alert-button-md alert-button-default alert-button-default-md']")
				#boton.click()
				#flag_click = 1
			#except:
				#pass

		# Realizar una espera antes de cada solicitud
		# sleep(2)

		flag_click = 0
		account = 0
		while(flag_click == 0):
			try:
				copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='slideSportsTab-item']/i[@class='icon-tennis']")))
				driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
				link = driver.find_element_by_xpath("//div[@class='slideSportsTab-item']/i[@class='icon-tennis']")
				link.click()
				flag_click = 1
			except:
				account += 1
				if account == 50:
					sleep(500)
					account = 0
				pass

		# Realizar una espera antes de cada solicitud
		sleep(2)

		# Bucle principal del hilo de codere
		# XPATH (//event-card/ion-card/ion-card-content/div[@class='market-header'])[1]/button/span/i
		while self.seguir == True:
			dinero_codere_element = driver.find_element_by_xpath("(//ion-buttons[@class='loginOps align-right user-actions bar-buttons bar-buttons-md']/div)[2]//button[@class='nav-item bar-button bar-button-md bar-button-default bar-button-default-md']/span[@class='button-inner']")
			dinero_codere = dinero_codere_element.text
			if(float(dinero_codere[:len(dinero_codere) - 1].replace(",",".")) < 30):
				print("Codere no dispone de dinero, no se van a realizar apuestas")
				self.seguir = False
			else:
				print("Codere dispone de dinero, se realizan apuestas, dinero codere-> " + dinero_codere[:len(dinero_codere) - 1])
				link_partidos = driver.find_elements_by_xpath("//event-card")
				tamanio_partidos = len(link_partidos)
				j  = 0
				boton_raro = 0
				while(j < tamanio_partidos):
					boton_raro += 1
					xpath = "//event-card[" + str(j + 1) + "]/ion-card/ion-card-content/div[@class='market-header']/div/h1"
					try:
						link_partido = driver.find_element_by_xpath(xpath)
						participantes = link_partido.text.split("-")
					except:
						participantes = []
						participantes.append("Hola, soy un valor por defecto")

					self.cola2.put(participantes[0].encode("utf-8", "latin-1").lower())
					flag_click = 0
					while(flag_click == 0):
						try:
							copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//event-card[" + str(j + 1)+ "]/ion-card/ion-card-content/div[@class='market-header']/button/span/i")))
							driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
							driver.find_element_by_xpath("//event-card[" + str(j + 1)+ "]/ion-card/ion-card-content/div[@class='market-header']/button/span/i").click()
							flag_click = 1
						except:
							if(boton_raro == 50):
								try:
									continuar = driver.find_element_by_xpath("//button[@class='alert-button alert-button-md alert-button-default alert-button-default-md']/span")
									continuar.click()
									flag_click = 1
								except:
									pass
							pass
					check = self.cola1.get()

					# Eperamos a que bet encuentre el partido que codere ha encontrado
					if check == True:

						# Realizar una espera antes de cada solicitud
						sleep(2)
						try:
							link_apuestas = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card")
							tamanio = len(link_apuestas)
						except:
							pass
						k = 0
						# A la hora de realizar las apuestas hacerlo justo deespues del codigo de todos los tipos de apuesta para no pasar por codigo innecesario
						while(k < tamanio):
							account = 0
							try:
								comprobar = 0
								link_apuesta = driver.find_element_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/ion-card-content/ion-grid/ion-row/ion-col/h1")
								texto_apuesta = link_apuesta.text.split(" ")
								# Apuesta de tipo ganador del partido
								if (len(texto_apuesta) == 3 and texto_apuesta[0] == "Ganador" and texto_apuesta[1] == "del" and texto_apuesta[2] == "partido"):
									string = "Ganara"
									self.cola2.put([string])
									# Proceso de apertura de la apuesta si esta cerrada
									flag_click = 0
									link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
									if(link_apuesta):
										flag_click = 0
										while(flag_click == 0):
											try:
												copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
												driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
												link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
												link_cerrado.click()
												flag_click = 1
											except:
												pass
									# Proceso de obtencion de cotizaciones
									cotizaciones_link = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
									try:
										cotizaciones = [cotizaciones_link[0].text, cotizaciones_link[1].text]
									except StaleElementReferenceException:
										cotizaciones = [":(", ":("]

									check = self.cola1.get()
									if(check == True):
										self.cola5.put(cotizaciones)
										# Proceso de comprobacion de sure bet
										datos = self.cola6.get()

										# Estamos ante una apuesta segura
										# Aqui hay que hacer apuesta
										if datos[0] == True:
											apuesta1 = datos[1]
											apuesta2 = datos[2]
											# Hay que apostar por el segundo jugador
											if apuesta1 == 0:
												try:
													flag_click = 0
													while(flag_click == 0):
														try:
															link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
															if(link_apuesta):
																flag_click = 0
																while(flag_click == 0):
																	try:
																		copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
																		driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
																		link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
																		link_cerrado.click()
																		flag_click = 1
																	except:
																		pass
															#copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")))
															#driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
															apostar = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
															apostar[1].click()
															print("Se ha hecho click correctamente")
															flag_click = 1
														except:
															pass
													
													print("Codere-> Estamos en el caso de que hay que apostar por el segundo jugador con tipo de apuesta ganador del partido")
													print("Codere-> Pasamos ahora a comprobar si los datos son correctos en codere")
													flag_click = 0
													contador = 0
													while(flag_click == 0):
														try:
															jugador = driver.find_element_by_xpath("//span[@class='nameAp-title is-bold']")
															flag_click = 1
														except:
															contador += 1
															if contador == 20:
																flag_click = 1
															pass
													print("Codere-> Comparando " + jugador.text.lower() + " con " + participantes[0].lower())
													if(similar(jugador.text.lower(), participantes[0].lower()) < 0.7):
														print("Codere-> Jugador comprobado correctamente")
														todo_correcto = True
													else:
														todo_correcto = False
													apostar = driver.find_element_by_xpath("//p[@class='typeAp']")
													comparar = "Ganador del partido"
													print("Codere-> Comparando " + str(apostar.text) + " con "  + comparar)
													if (str(apostar.text) == comparar):
														print("Codere-> Tipo de apuesta correcto")
													else:
														todo_correcto = False
														print("Codere-> Tipo de apuesta incorrecta")
													cotizacion = driver.find_element_by_xpath("//span[@class='nameAp']/b")
													print("Codere-> Comparando " + str(cotizacion.text) + " con " + cotizaciones[1])
													if (float(cotizacion.text.replace(",", ".")) >= float(cotizaciones[1].replace(",","."))):
														print("Codere-> Cotizacion correcta")
													else:
														todo_correcto = False
														print("Codere-> Cotizacion incorrecta")
													# Aqui confirmamos a bet
													if todo_correcto == True:
														print("Codere-> Todo correcto, procedemos a apostar")
														dinero = driver.find_element_by_xpath("(//div[@class='ticket-input-wrapper']/ion-input)[3]/input")
														dinero.send_keys(Keys.BACK_SPACE)
														dinero.send_keys(str(apuesta2))
														#ActionChains(driver).move_to_element(dinero).click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(str(apuesta2)).perform()
														print("Soy codere y voy a apostar " + str(apuesta2))
														self.cola2.put(True)
														comprobacion = self.cola1.get()
														# Aqui realizariamos apuesta
														if (comprobacion == True):
															print("Codere realizaria apuesta, porque bet confirma")
															s.call(['notify-send','Codere','Sure Bet encontrada'])
															flag_click = 0
															while(flag_click == 0):
																try:
																	aceptar = driver.find_element_by_xpath("(//button[@class='is-ticket-button endAp'])[2]/p")
																	aceptar.click()
																	flag_click = 1
																	print("Codere ha realizado apuesta")
																except Exception as e:
																	print("Error al apostar codere-> " + str(e))
																	print("Codere no ha realizado apuesta")
																	pass
														else:
															print("Codere no realiza apuesta porque bet no confirma")
															# En vez de realizar quitamos la apuesta
															flag_click = 0
															while(flag_click == 0):
																try:
																	cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																	cancelar.click()
																	flag_click = 1
																except:
																	pass
													else:
														print("Codere-> Error en la comprobacion, no se va a realizar ninguna apuesta")
														self.cola2.put(False)
														descartar = self.cola1.get()
														flag_click = 0
														while(flag_click == 0):
															try:
																cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																cancelar.click()
																flag_click = 1
															except:
																pass
												except Exception as e:
													print("Codere-> Se ha producido un error comprobando apuestas, cancelamos")
													print(e)
													flag_click = 0
													contador = 0
													while(flag_click == 0):
														try:
															cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
															cancelar.click()
															flag_click = 1
														except:
															contador += 1
															if (contador == 50):
																flag_click = 1
															pass

											# Hay que apostar por el primer jugador
											else:
												try:
													flag_click = 0
													while(flag_click == 0):
														try:
															link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
															if(link_apuesta):
																flag_click = 0
																while(flag_click == 0):
																	try:
																		copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
																		driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
																		link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
																		link_cerrado.click()
																		flag_click = 1
																	except:
																		pass
															#copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")))
															#driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
															apostar = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
															apostar[0].click()
															print("Se ha hecho click correctamente")
															flag_click = 1
														except:
															pass
													
													print("Codere-> Estamos en el caso de que hay que apostar por el primer jugador con tipo de apuesta ganador del partido")
													print("Codere-> Pasamos ahora a comprobar si los datos son correctos en codere")
													flag_click = 0
													contador = 0
													while(flag_click == 0):
														try:
															jugador = driver.find_element_by_xpath("//span[@class='nameAp-title is-bold']")
															flag_click = 1
														except:
															contador += 1
															if contador == 20:
																flag_click = 1
															pass
													print("Codere-> Comparando " + jugador.text.lower() + " con " + participantes[0].lower())
													if(similar(jugador.text.lower(), participantes[0].lower()) > 0.7):
														print("Codere-> Jugador comprobado correctamente")
														todo_correcto = True
													else:
														todo_correcto = False
													apostar = driver.find_element_by_xpath("//p[@class='typeAp']")
													comparar = "Ganador del partido"
													print("Codere-> Comparando " + str(apostar.text) + " con " + comparar)
													if (str(apostar.text) == comparar):
														print("Codere-> Tipo de apuesta correcto")
													else:
														todo_correcto = False
														print("Codere-> Tipo de apuesta incorrecta")
													cotizacion = driver.find_element_by_xpath("//span[@class='nameAp']/b")
													print("Codere-> Comparando " + str(cotizacion.text) + " con " + cotizaciones[0])
													if (float(cotizacion.text.replace(",", ".")) >= float(cotizaciones[0].replace(",","."))):
														print("Codere-> Cotizacion correcta")
													else:
														todo_correcto = False
														print("Codere-> Cotizacion incorrecta")
													if todo_correcto == True:
														print("Codere-> Todo correcto, procedemos a apostar")
														dinero = driver.find_element_by_xpath("(//div[@class='ticket-input-wrapper']/ion-input)[3]/input")
														dinero.send_keys(Keys.BACK_SPACE)
														dinero.send_keys(str(apuesta1))
														#ActionChains(driver).move_to_element(dinero).click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(str(apuesta1)).perform()
														print("Soy codere y voy a apostar " + str(apuesta1))
														# Aqui confirmamos a bet
														self.cola2.put(True)
														comprobacion = self.cola1.get()
														# Aqui realizariamos apuesta
														if (comprobacion == True):
															print("Codere realizaria apuesta porque bet confirma")
															s.call(['notify-send','Codere','Sure Bet encontrada'])
															flag_click = 0
															while(flag_click == 0):
																try:
																	aceptar = driver.find_element_by_xpath("(//button[@class='is-ticket-button endAp'])[2]/p")
																	aceptar.click()
																	flag_click = 1
																	print("Codere ha realizado apuesta")
																except Exception as e:
																	print("Error al apostar codere-> " + str(e))
																	print("Codere no ha realizado apuesta")
																	pass
														else:
															print("Codere no realiza apuesta porque bet no confirma")
															# En vez de realizar quitamos la apuesta
															flag_click = 0
															while(flag_click == 0):
																try:
																	cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																	cancelar.click()
																	flag_click = 1
																except:
																	pass
													else:
														print("Codere-> Error en la comprobacion, no se va a realizar ninguna apuesta")
														self.cola2.put(False)
														descartar = self.cola1.get()
														flag_click = 0
														while(flag_click == 0):
															try:
																cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																cancelar.click()
																flag_click = 1
															except:
																pass
														print("Codere-> Cancelacion correcta")
												except Exception as e:
													print("Codere-> Se ha producido un error comprobando apuestas, cancelamos")
													print(e)
													flag_click = 0
													contador = 0
													while(flag_click == 0):
														try:
															cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
															cancelar.click()
															flag_click = 1
														except:
															contador += 1
															if (contador == 50):
																flag_click = 1
															pass
													self.cola2.put(False)
													descartar = self.cola1.get()

												

								# Apuesta de tipo ganador de test
								elif (texto_apuesta[2] == "Set" and texto_apuesta[1] != "Final"):
									xpath_aux = "//ion-row[@class = 'rowTitTable row']/ion-col[1]"
									numero_set = driver.find_element_by_xpath(xpath_aux)
									x = numero_set.text[0]
									# Si es el set actual
									if(texto_apuesta[3] == x):
										self.cola2.put(["Set", texto_apuesta[3], True])
									# Si no estamos en el set actual
									else:
										self.cola2.put(["Set", texto_apuesta[3], False])

									# Proceso de apertura de apuesta
									flag_click = 0
									link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
									if(link_apuesta):
										flag_click = 0
										while(flag_click == 0):
											try:
												copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
												driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
												link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
												link_cerrado.click()
												flag_click = 1
											except:
												pass
									# Guardamos cotizaciones
									cotizaciones_link = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
									try:
										cotizaciones = [cotizaciones_link[0].text, cotizaciones_link[1].text]
									except StaleElementReferenceException:
										cotizaciones = [":(", ":("]

									check = self.cola1.get()
									if (check == True):
										self.cola5.put(cotizaciones)
										# Proceso de comprobacion de sure bet
										datos = self.cola6.get()

										# Estamos ante una apuesta segura
										# Aqui hay que hacer apuesta
										if datos[0] == True:
											apuesta1 = datos[1]
											apuesta2 = datos[2]
						
											if apuesta1 == 0:
												try:
													flag_click = 0
													while(flag_click == 0):
														try:
															link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
															if(link_apuesta):
																flag_click = 0
																while(flag_click == 0):
																	try:
																		copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
																		driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
																		link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
																		link_cerrado.click()
																		flag_click = 1
																	except:
																		pass
															#copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")))
															#driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
															apostar = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
															apostar[1].click()
															print("Se ha hecho click correctamente")
															flag_click = 1
														except:
															pass
													
													
													print("Codere-> Estamos en el caso de que hay que apostar por el segundo jugador con tipo de apuesta ganador de set")
													print("Codere-> Pasamos ahora a comprobar si los datos son correctos en codere")
													flag_click = 0
													contador = 0
													while(flag_click == 0):
														try:
															jugador = driver.find_element_by_xpath("//span[@class='nameAp-title is-bold']")
															flag_click = 1
														except:
															contador += 1
															if contador == 20:
																flag_click = 1
															pass
													print("Codere-> Comparando " + jugador.text.lower() + " con " + participantes[0].lower())
													if(similar(jugador.text.lower(), participantes[0].lower()) < 0.7):
														print("Codere-> Jugador comprobado correctamente")
														todo_correcto = True
													else:
														todo_correcto = False
													apostar = driver.find_element_by_xpath("//p[@class='typeAp']")
													comparar = "Ganador del Set " + texto_apuesta[3]
													print("Codere-> Comparando " + str(apostar.text) + " con " + comparar)
													if (str(apostar.text) == comparar):
														print("Codere-> Tipo de apuesta correcto")
													else:
														todo_correcto = False
														print("Codere-> Tipo de apuesta incorrecta")
													cotizacion = driver.find_element_by_xpath("//span[@class='nameAp']/b")
													print("Codere-> Comparando " + str(cotizacion.text) + " con " + cotizaciones[1])
													if (float(cotizacion.text.replace(",", ".")) >= float(cotizaciones[1].replace(",","."))):
														print("Codere-> Cotizacion correcta")
													else:
														todo_correcto = False
														print("Codere-> Cotizacion incorrecta")
													# Aqui confirmamos a bet
													if todo_correcto == True:
														print("Codere-> Todo correcto, procedemos a apostar")
														dinero = driver.find_element_by_xpath("(//div[@class='ticket-input-wrapper']/ion-input)[3]/input")
														dinero.send_keys(Keys.BACK_SPACE)
														dinero.send_keys(str(apuesta2))
														#ActionChains(driver).move_to_element(dinero).click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(str(apuesta2)).perform()
														print("Soy codere y voy a apostar " + str(apuesta2))
														self.cola2.put(True)
														comprobacion = self.cola1.get()
														# Aqui realizariamos apuesta
														if (comprobacion == True):
															print("Codere realizaria apuesta porque bet confirma")
															s.call(['notify-send','Codere','Sure Bet encontrada'])
															flag_click = 0
															while(flag_click == 0):
																try:
																	aceptar = driver.find_element_by_xpath("(//button[@class='is-ticket-button endAp'])[2]/p")
																	aceptar.click()
																	flag_click = 1
																	print("Codere ha realizado apuesta")
																except Exception as e:
																	print("Error al apostar codere-> " + str(e))
																	print("Codere no ha realizado apuesta")
																	pass
														else:
															print("Codere no realiza apuesta porque bet no confirma")
															# En vez de realizar quitamos la apuesta
															flag_click = 0
															while(flag_click == 0):
																try:
																	cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																	cancelar.click()
																	flag_click = 1
																except:
																	pass
													else:
														print("Codere-> Error en la comprobacion, no se va a realizar ninguna apuesta")
														self.cola2.put(False)
														descartar = self.cola1.get()
														flag_click = 0
														while(flag_click == 0):
															try:
																cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																cancelar.click()
																flag_click = 1
															except:
																pass
												except Exception as e:
													print("Codere-> Se ha producido un error comprobando apuestas, cancelamos")
													print(e)
													flag_click = 0
													contador = 0
													while(flag_click == 0):
														try:
															cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
															cancelar.click()
															flag_click = 1
														except:
															contador += 1
															if (contador == 50):
																flag_click = 1
															pass
													self.cola2.put(False)
													descartar = self.cola1.get()

											# Hay que apostar por el primer jugador
											else:
												try:
													flag_click = 0
													while(flag_click == 0):
														try:
															link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
															if(link_apuesta):
																flag_click = 0
																while(flag_click == 0):
																	try:
																		copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
																		driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
																		link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
																		link_cerrado.click()
																		flag_click = 1
																	except:
																		pass
															#copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")))
															#driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
															apostar = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
															apostar[0].click()
															print("Se ha hecho click correctamente")
															flag_click = 1
														except:
															pass
													
													print("Codere-> Estamos en el caso de que hay que apostar por el primer jugador con tipo de apuesta ganador de set")
													print("Codere-> Pasamos ahora a comprobar si los datos son correctos en codere")
													flag_click = 0
													contador = 0
													while(flag_click == 0):
														try:
															jugador = driver.find_element_by_xpath("//span[@class='nameAp-title is-bold']")
															flag_click = 1
														except:
															contador += 1
															if contador == 20:
																flag_click = 1
															pass
													print("Codere-> Comparando " + jugador.text.lower() + " con " + participantes[0].lower())
													if(similar(jugador.text.lower(), participantes[0].lower()) > 0.7):
														print("Codere-> Jugador comprobado correctamente")
														todo_correcto = True
													else:
														todo_correcto = False
													apostar = driver.find_element_by_xpath("//p[@class='typeAp']")
													comparar = "Ganador del Set " + texto_apuesta[3]
													print("Codere-> Comparando " + str(apostar.text) + " con " + comparar)
													if (str(apostar.text) == comparar):
														print("Codere-> Tipo de apuesta correcto")
													else:
														todo_correcto = False
														print("Codere-> Tipo de apuesta incorrecta")
													cotizacion = driver.find_element_by_xpath("//span[@class='nameAp']/b")
													print("Codere-> Comparando " + str(cotizacion.text) + " con " + cotizaciones[0])
													if (float(cotizacion.text.replace(",", ".")) >= float(cotizaciones[0].replace(",","."))):
														print("Codere-> Cotizacion correcta")
													else:
														todo_correcto = False
														print("Codere-> Cotizacion incorrecta")
													# Aqui confirmamos a bet
													if todo_correcto == True:
														print("Codere-> Todo correcto, procedemos a apostar")
														dinero = driver.find_element_by_xpath("(//div[@class='ticket-input-wrapper']/ion-input)[3]/input")
														dinero.send_keys(Keys.BACK_SPACE)
														dinero.send_keys(str(apuesta1))
														#ActionChains(driver).move_to_element(dinero).click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(str(apuesta1)).perform()
														print("Soy codere y voy a apostar " + str(apuesta1))
														self.cola2.put(True)
														comprobacion = self.cola1.get()
														# Aqui realizariamos apuesta
														if (comprobacion == True):
															print("Codere realizaria apuesta, porque bet confirma")
															s.call(['notify-send','Codere','Sure Bet encontrada'])
															flag_click = 0
															while(flag_click == 0):
																try:
																	aceptar = driver.find_element_by_xpath("(//button[@class='is-ticket-button endAp'])[2]/p")
																	aceptar.click()
																	flag_click = 1
																	print("Codere ha realizado apuesta")
																except Exception as e:
																	print("Error al apostar codere-> " + str(e))
																	print("Codere no ha realizado apuesta")
																	pass
														else:
															print("Codere no realiza apuesta porque bet no confirma")
															flag_click = 0
															while(flag_click == 0):
																try:
																	cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																	cancelar.click()
																	flag_click = 1
																except:
																	pass
													else:
														print("Codere-> Error en la comprobacion, no se va a realizar ninguna apuesta")
														self.cola2.put(False)
														descartar = self.cola1.get()
														flag_click = 0
														while(flag_click == 0):
															try:
																cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																cancelar.click()
																flag_click = 1
															except:
																pass
												except Exception as e:
													print("Codere-> Se ha producido un error comprobando apuestas, cancelamos")
													print(e)
													flag_click = 0
													contador = 0
													while(flag_click == 0):
														try:
															cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
															cancelar.click()
															flag_click = 1
														except:
															contador += 1
															if (contador == 50):
																flag_click = 1
															pass
													self.cola2.put(False)
													descartar = self.cola1.get()

								else:
									texto_juego = driver.find_elements_by_xpath("//ion-row[@class='rowContTable row']/ion-col[not(contains(@class,'liveResultSet col serve') or contains(@class,'liveResultSet col'))]")
									juego = 0
									cuenta = 0
									for juego_numero in texto_juego:
										cuenta += 1
										if(cuenta != len(texto_juego)/2 and cuenta != len(texto_juego)):
											try:
												a = float(juego_numero.text)
												juego = juego + a
											except ValueError:
												pass

									# Apuesta de tipo ganador de punto
									# Lo dejo marcado abajo, vamos a hacer pruebas sin ganador de punto
		
									# Apuesta de tipo ganador de juego
									if (texto_apuesta[1] == "Juego"):
										juego_apuesta = juego + float(texto_apuesta[2])
										self.cola2.put(["Juego", str(juego_apuesta)])
										# Proceso de apertura de apuesta
										flag_click = 0
										link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
										if(link_apuesta):
											flag_click = 0
											while(flag_click == 0):
												try:
													copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
													driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
													link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
													link_cerrado.click()
													flag_click = 1
												except:
													pass
										# Guardamos cotizaciones
										cotizaciones_link = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
										try:
											cotizaciones = [cotizaciones_link[0].text, cotizaciones_link[1].text]
										except StaleElementReferenceException:
											cotizaciones = [":(", ":("]

										check = self.cola1.get()
										if (check == True):
											# Proceso de obtencion de cotizaciones
											self.cola5.put(cotizaciones)
											# Proceso de comprobacion de sure bet
											datos = self.cola6.get()

											# Estamos ante una apuesta segura
											# Aqui hay que hacer apuesta
											if datos[0] == True:
												apuesta1 = datos[1]
												apuesta2 = datos[2]
												
												if apuesta1 == 0:
													try:
														flag_click = 0
														while(flag_click == 0):
															try:
																link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
																if(link_apuesta):
																	flag_click = 0
																	while(flag_click == 0):
																		try:
																			copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
																			driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
																			link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
																			link_cerrado.click()
																			flag_click = 1
																		except:
																			pass
																#copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")))
																#driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
																apostar = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
																apostar[1].click()
																print("Se ha hecho click correctamente")
																flag_click = 1
															except:
																pass
														print("Codere-> Estamos en el caso de que hay que apostar por el segundo jugador con tipo de apuesta ganador de juego")
														print("Codere-> Pasamos ahora a comprobar si los datos son correctos en codere")
														flag_click = 0
														contador = 0
														while(flag_click == 0):
															try:
																jugador = driver.find_element_by_xpath("//span[@class='nameAp-title is-bold']")
																flag_click = 1
															except:
																contador += 1
																if contador == 20:
																	flag_click = 1
																pass
														print("Codere-> Comparando " + jugador.text.lower() + " con " + participantes[0].lower())
														if(similar(jugador.text.lower(), participantes[0].lower()) < 0.7):
															print("Codere-> Jugador comprobado correctamente")
															todo_correcto = True
														else:
															todo_correcto = False
														apostar = driver.find_element_by_xpath("//p[@class='typeAp']")
														comparar = "Ganador Juego " + texto_apuesta[2] + " del Set " + texto_apuesta[5] 
														print("Codere-> Comparando " + str(apostar.text) + " con " + comparar)
														print(texto_apuesta)
														if (str(apostar.text) == comparar):
															print("Codere-> Tipo de apuesta correcto")
														else:
															todo_correcto = False
															print("Codere-> Tipo de apuesta incorrecta")
														cotizacion = driver.find_element_by_xpath("//span[@class='nameAp']/b")
														print("Codere-> Comparando " + str(cotizacion.text) + " con " + cotizaciones[1])
														if (float(cotizacion.text.replace(",", ".")) >= float(cotizaciones[1].replace(",","."))):
															print("Codere-> Cotizacion correcta")
														else:
															todo_correcto = False
															print("Codere-> Cotizacion incorrecta")
														# Aqui confirmamos a bet
														if todo_correcto  == True:
															print("Codere-> Todo correcto, procedemos a apostar")
															dinero = driver.find_element_by_xpath("(//div[@class='ticket-input-wrapper']/ion-input)[3]/input")
															dinero.send_keys(Keys.BACK_SPACE)
															dinero.send_keys(str(apuesta2))
															#ActionChains(driver).move_to_element(dinero).click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(str(apuesta2)).perform()
															print("Soy codere y voy a apostar " + str(apuesta2))
															self.cola2.put(True)
															comprobacion = self.cola1.get()
															# Aqui realizariamos apuesta
															if (comprobacion == True):
																print("Codere realizaria apuesta, porque bet confirma")
																s.call(['notify-send','Codere','Sure Bet encontrada'])
																flag_click = 0
																while(flag_click == 0):
																	try:
																		aceptar = driver.find_element_by_xpath("(//button[@class='is-ticket-button endAp'])[2]/p")
																		aceptar.click()
																		flag_click = 1
																		print("Codere ha realizado apuesta")
																	except Exception as e:
																		print("Error al apostar codere-> " + str(e))
																		print("Codere no ha realizado apuesta")
																		pass
															else:
																print("Codere no realiza apuesta porque bet no confirma")
																# En vez de realizar quitamos la apuesta
																flag_click = 0
																while(flag_click == 0):
																	try:
																		cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																		cancelar.click()
																		flag_click = 1
																	except:
																		pass
														else:
															print("Codere-> Se ha producido un error comprobando apuestas, cancelamos")
															self.cola2.put(False)
															descartar = self.cola1.get()
															flag_click = 0
															while(flag_click == 0):
																try:
																	cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																	cancelar.click()
																	flag_click = 1
																except:
																	pass
													except Exception as e:
														print("Codere-> Se ha producido un error comprobando apuestas, cancelamos")
														print(e)
														flag_click = 0
														contador = 0
														while(flag_click == 0):
															try:
																cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																cancelar.click()
																flag_click = 1
															except:
																contador += 1
																if (contador == 50):
																	flag_click = 1
																pass
														self.cola2.put(False)
														descartar = self.cola1.get()

												# Hay que apostar por el primer jugador
												else:
													try:
														flag_click = 0
														while(flag_click == 0):
															try:
																link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
																if(link_apuesta):
																	flag_click = 0
																	while(flag_click == 0):
																		try:
																			copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
																			driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
																			link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
																			link_cerrado.click()
																			flag_click = 1
																		except:
																			pass
																#copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")))
																#driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
																apostar = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
																apostar[0].click()
																print("Se ha hecho click correctamente")
																flag_click = 1
															except:
																pass
														print("Codere-> Estamos en el caso de que hay que apostar por el primer jugador con tipo de apuesta ganador de juego")
														print("Codere-> Pasamos ahora a comprobar si los datos son correctos en codere")
														flag_click = 0
														contador = 0
														while(flag_click == 0):
															try:
																jugador = driver.find_element_by_xpath("//span[@class='nameAp-title is-bold']")
																flag_click = 1
															except:
																contador += 1
																if contador == 20:
																	flag_click = 1
																pass
														print("Codere-> Comparando " + jugador.text.lower() + " con " + participantes[0].lower())
														if(similar(jugador.text.lower(), participantes[0].lower()) > 0.7):
															print("Codere-> Jugador comprobado correctamente")
															todo_correcto = True
														else:
															todo_correcto = False
														apostar = driver.find_element_by_xpath("//p[@class='typeAp']")
														comparar = "Ganador Juego " + texto_apuesta[2] + " del Set " + texto_apuesta[5]
														print(texto_apuesta)
														print("Codere-> Comparando " + str(apostar.text) + " con " + comparar)
														if (str(apostar.text) == comparar):
															print("Codere-> Tipo de apuesta correcto")
														else:
															todo_correcto = False
															print("Codere-> Tipo de apuesta incorrecta")
														cotizacion = driver.find_element_by_xpath("//span[@class='nameAp']/b")
														print("Codere-> Comparando " + str(cotizacion.text) + " con " + cotizaciones[0])
														if (float(cotizacion.text.replace(",", ".")) >= float(cotizaciones[0].replace(",","."))):
															print("Codere-> Cotizacion correcta")
														else:
															todo_correcto = False
															print("Codere-> Cotizacion incorrecta")
														# Aqui confirmamos a bet
														if todo_correcto == True:
															print("Codere-> Todo correcto, procedemos a apostar")
															dinero = driver.find_element_by_xpath("(//div[@class='ticket-input-wrapper']/ion-input)[3]/input")
															dinero.send_keys(Keys.BACK_SPACE)
															dinero.send_keys(str(apuesta1))
															#ActionChains(driver).move_to_element(dinero).click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(str(apuesta1)).perform()
															print("Soy codere y voy a apostar " + str(apuesta1))
															self.cola2.put(True)
															comprobacion = self.cola1.get()
															# Aqui realizariamos apuesta
															if (comprobacion == True):
																print("Codere realizaria apuesta, porque bet confirma")
																s.call(['notify-send','Codere','Sure Bet encontrada'])
																flag_click = 0
																while(flag_click == 0):
																	try:
																		aceptar = driver.find_element_by_xpath("(//button[@class='is-ticket-button endAp'])[2]/p")
																		aceptar.click()
																		flag_click = 1
																		print("Codere ha realizado apuesta")
																	except Exception as e:
																		print("Error al apostar codere-> " + str(e))
																		print("Codere no ha realizado apuesta")
																		pass

															else:
																print("Codere no realiza apuesta porque bet no confirma")
																# En vez de realizar quitamos la apuesta
																flag_click = 0
																while(flag_click == 0):
																	try:
																		cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																		cancelar.click()
																		flag_click = 1
																	except:
																		pass
														else:
															print("Codere-> Se ha producido un error comprobando apuestas, cancelamos")
															self.cola2.put(False)
															descartar = self.cola1.get()
															flag_click = 0
															while(flag_click == 0):
																try:
																	cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																	cancelar.click()
																	flag_click = 1
																except:
																	pass
													except Exception as e:
														print("Codere-> Se ha producido un error comprobando apuestas, cancelamos")
														print(e)
														flag_click = 0
														contador = 0
														while(flag_click == 0):
															try:
																cancelar = driver.find_element_by_xpath("(//button[@class='deleteAll button button-md button-clear button-clear-md button-full button-full-md'])[2]/span")
																cancelar.click()
																flag_click = 1
															except:
																contador += 1
																if (contador == 50):
																	flag_click = 1
																pass
														self.cola2.put(False)
														descartar = self.cola1.get()


							except:
								# Caso en el que salta el error de partido no disponible
								if(account == 20):
									try:
										continuar = driver.find_element_by_xpath("//button[@class='alert-button alert-button-md alert-button-default alert-button-default-md']/span")
										continuar.click()
									except:
										pass
								pass

							k += 1
							link_apuestas = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card")
							tamanio = len(link_apuestas)

						# No nos valen mas tipos de apuestas, pasamos al siguiente jugador
						self.cola2.put(["Continuar"])
						check = self.cola1.get()
						if(check == False):
							print("Se ha producido un error")
							self.seguir = False

						# Volvemos a clickar en directo y en tenis
						flag_click = 0
						while(flag_click == 0):
							try:
								link = driver.find_element_by_xpath("(//div[@class='nav left navSectionsNavbar'])[2]//ion-buttons/button[@class='nav-item bar-button bar-button-md bar-button-default bar-button-default-md'][position() = 2]")
								link.click()
								flag_click = 1
							except:
								pass

						sleep(2)

						flag_click = 0
						account = 0
						while(flag_click == 0):
							try:
								link = driver.find_element_by_xpath("//div[@class='slideSportsTab-item']/i[@class='icon-tennis']")
								link.click()
								sleep(1)
								flag_click = 1
							except:
								link = driver.find_elements_by_xpath("//div[@class='slideSportsTab-item selected']/i[@class='icon-tennis']")
								if(len(link) == 1):
									flag_click = 1
								else:
									if (account == 50):
										sleep(500)
										account = 0
									try:
										copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='slideSportsTab-item']/i[@class='icon-tennis']")))
										driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
										link = driver.find_element_by_xpath("//div[@class='slideSportsTab-item']/i[@class='icon-tennis']")
										link.click()
										flag_click = 1
									except:
										account += 1
										sleep(1)
					else:
						sleep(1)
						flag_click = 0
						while(flag_click == 0):
							try:
								link = driver.find_element_by_xpath("(//div[@class='nav left navSectionsNavbar'])[2]//ion-buttons/button[@class='nav-item bar-button bar-button-md bar-button-default bar-button-default-md'][position() = 2]")
								link.click()
								flag_click = 1
							except:
								pass

						sleep(2)

						flag_click = 0
						account = 0
						while(flag_click == 0):
							try:
								link = driver.find_element_by_xpath("//div[@class='slideSportsTab-item']/i[@class='icon-tennis']")
								link.click()
								sleep(1)
								flag_click = 1
							except:
								link = driver.find_elements_by_xpath("//div[@class='slideSportsTab-item selected']/i[@class='icon-tennis']")
								if(len(link) == 1):
									flag_click = 1
								else:
									if (account == 50):
										sleep(500)
										account = 0
									try:
										copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='slideSportsTab-item']/i[@class='icon-tennis']")))
										driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
										link = driver.find_element_by_xpath("//div[@class='slideSportsTab-item']/i[@class='icon-tennis']")
										link.click()
										flag_click = 1
									except:
										account += 1
										sleep(1)
						

					j += 1
					link_partidos = driver.find_elements_by_xpath("//event-card")
					tamanio_partidos = len(link_partidos)


	# Funcion que cambia la variable seguir a false y para el hilo
	def parar(self):
		self.seguir = False

#def realizar_apuesta_codere():

# Funcion que devuelve la similitud entre una cadena y otra
# Fcking python3, hay que repasar esta mierda
def similar(a, b):
	a_aux = a.replace(" (svr)", "").replace(" - servicio", "")
	b_aux = b.replace(" (svr)", "").replace(" - servicio", "")
	a = ngram.NGram.compare(a_aux, b_aux, N=1)
	print("Comparando " + str(a_aux) + " y " + str(b_aux) + " = " + str(a))
	return a

def clean_string(cadena):
	cadena = cadena.replace("\xc3\xa1", "a")
	cadena = cadena.replace("\xc2\xbf", " ")
	cadena = cadena.replace("\xc3\xa9", "e")
	cadena = cadena.replace("\xc3\xad", "i")
	cadena = cadena.replace("\xc3\xb3", "o")
	cadena = cadena.replace("\xc3\xba", "u")
	return cadena


#Ganador de punto
def punto():
	if texto_apuesta[2] == "Punto":
		juego_apuesta = juego + float(texto_apuesta[7])
		self.cola2.put(["Punto", str(juego_apuesta), texto_apuesta[3]])
		# Proceso de apertura de apuesta
		flag_click = 0
		link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
		if(link_apuesta):
			flag_click = 0
			while(flag_click == 0):
				try:
					copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
					driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
					link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
					link_cerrado.click()
					flag_click = 1
				except:
					pass
		# Guardamos cotizaciones
		cotizaciones_link = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
		try:
			cotizaciones = [cotizaciones_link[0].text, cotizaciones_link[1].text]
		except StaleElementReferenceException:
			cotizaciones = [":(", ":("]

		check = self.cola1.get()
		# Si bet encuentra la apuesta enviamos las cotizaciones
		if (check == True):
			self.cola5.put(cotizaciones)
			# Proceso de comprobacion de sure bet
			datos = self.cola6.get()

			# Estamos ante una apuesta segura
			# Aqui hay que hacer apuesta
			if datos[0] == True:
				apuesta1 = datos[1]
				apuesta2 = datos[2]
				fichero_bet = open("SURE_BET/sure_codere_" + str(numero_sure_bet) + ".html", "w")
				fichero_bet.write(driver.page_source)
				# sleep(1)
				fichero_bet.close()
				numero_sure_bet += 1

		#Handicap
		# Apuesta de tipo handicap por juegos
		elif (len(texto_apuesta) == 3 and texto_apuesta[0].encode("latin-1") == u"H\xc3\xa1ndicap" and texto_apuesta[1] ==  "por" and texto_apuesta[2] == "juegos"):
			string = "Encuentro"
			self.cola2.put([string])
			# Proceso de apertura de apuesta
			flag_click = 0
			link_apuesta = driver.find_elements_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
			if(link_apuesta):
				flag_click = 0
				while(flag_click == 0):
					try:
						copyright = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")))
						driver.execute_script("return arguments[0].scrollIntoView(true);", copyright)
						link_cerrado = driver.find_element_by_xpath("//ion-list[@class='events-list list list-md']/div/market-card[" + str(k + 1) + "]/ion-card[@class='market-card animated card card-md collapsed listadoMercado']")
						link_cerrado.click()
						flag_click = 1
					except:
						pass
			# Guardamos cotizaciones
			cotizaciones_link = driver.find_elements_by_xpath("(//ion-list[@class='events-list list list-md']/div/market-card)[" + str(k + 1) + "]/ion-card/div/ion-grid/ion-row/ion-col/button/span/span")
			try:
				cotizaciones = [cotizaciones_link[0].text, cotizaciones_link[1].text]
			except StaleElementReferenceException:
				cotizaciones = [":(", ":("]

			check = self.cola1.get()
			if (check == True):
				self.cola5.put(cotizaciones)
				# Proceso de comprobacion de sure bet
				datos = self.cola6.get()

				# Estamos ante una apuesta segura
				# Aqui hay que hacer apuesta
				if datos[0] == True:
					apuesta1 = datos[1]
					apuesta2 = datos[2]
					#fichero_bet = open("SURE_BET/sure_codere_" + str(numero_sure_bet) + ".html", "w")
					#fichero_bet.write(driver.page_source)
					#fichero_bet.close()
					numero_sure_bet += 1


def iniciar_sesion(driverCodere, username, password):
	flag_click = 0
	while(flag_click == 0):
		try:
			acceder = driverCodere.find_element_by_xpath("//span[@class='btAccess cursorpoint']/span")
			acceder.click()
			flag_click = 1
		except:
			pass

	sleep(2)

	try:
		windowBefore = driverCodere.window_handles[0]
		windowAfter = driverCodere.window_handles[1]
		driverCodere.switch_to_window(windowAfter)
	except:
		pass

	sleep(2)
	flag_click = 0
	while(flag_click == 0):
		try:
			usuario = driverCodere.find_element_by_xpath("//input[@id='un']")
			# Introducir el nombre de usuario en lugar de las XXXX
			usuario.send_keys(username)
			flag_click = 1
		except:
			pass
	flag_click = 0
	while(flag_click == 0):
		try:
			contrasenia = driverCodere.find_element_by_xpath("//input[@id='pw']")
			# Introducir la contrasena en lugar de las XXXX
			contrasenia.send_keys(password)
			flag_click = 1
		except:
			pass
	flag_click = 0
	while(flag_click == 0):
		try:
			acceder = driverCodere.find_element_by_xpath("//div[@class='aceptarcuotabtn']")
			acceder.click()
			flag_click = 1
		except:
			pass
	driverCodere.switch_to_window(windowBefore)

