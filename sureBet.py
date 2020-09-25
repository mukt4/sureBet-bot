import queue
import argparse

from stats.estadistica import comprobar_cotizaciones
from stats.estadistica import similar
from crawler.tenis_betFair import ThreadBetFair
from crawler.tenis_bet import ThreadBet
from crawler.tenis_codere import ThreadCodere
from crawler.tenis_betV6 import ThreadBet2
from time import sleep

parser = argparse.ArgumentParser(prog='sureBet.py',
    	 description='Sure bet bot',
    	 formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=80))

parser.add_argument('-u1', '--user1', metavar='USER1', type=str,
    required=True, dest='user1', help='username/email(betting house 1)')

parser.add_argument('-p1', '--password1', metavar='PASS1', type=str,
    required=True, dest='password1', help='password(betting house 1)')

parser.add_argument('-u2', '--user2', metavar='USER2', type=str,
    required=True, dest='user2', help='username/email(betting house 2)')

parser.add_argument('-p2', '--password2', metavar='PASS2', type=str,
    required=True, dest='password2', help='password(betting house 2)')

parser.add_argument('-q', '--quantity', metavar='QUANTITY', type=int,
    required=True, dest='quantity', help='max bet')

parser.add_argument('-m', '--mode', metavar='MODE', type=int,
    required=True, dest='mode', help='mode(1-Bet365 and betfair, 2-Bet365 and codere)')

parser.add_argument('-b', '--benefits', metavar='BENEFITS', type=int,
    required=False, default=5, dest='benefits', help='percentage of benefits (5%% by default)')
 
parser.add_argument('-l', '--log', metavar='LOG', type=str,
    required=False, dest='log', help='save results in file')

args = parser.parse_args()

# Parse arguments
username1 = args.user1
password1 = args.password1
username2 = args.user2
password2 = args.password2
maximo = args.quantity
benefits= args.benefits
mode = args.mode

# Queue initialization
cola1 = queue.Queue()
cola2 = queue.Queue()
cola3 = queue.Queue()
cola4 = queue.Queue()
cola5 = queue.Queue()
cola6 = queue.Queue()

# Bet365 and betfair mode
if mode == 1:
	betFair = ThreadBetFair(cola1, cola2, username1, password1)
	bet = ThreadBet(cola1, cola2, username2, password2)
	betFair.start()
	bet.start()

# Bet365 and codere mode
elif mode == 2:
	codere = ThreadCodere(cola1, cola2, cola5, cola6, username1, password1)
	bet = ThreadBet2(cola1, cola2, cola3, cola4, username2, password2)
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
				print("SURE BET FOUND")
				fichero = open("SURE_BET/sure_full.txt", "a")
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
					print("SURE BET FOUND")
					fichero = open("SURE_BET/sure_full.txt", "a")
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
else:
	print("Incorrect mode")