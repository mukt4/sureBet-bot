import threading
import queue

from SCRAP.DESARROLLO.tenis_betFair import ThreadBetFair
from SCRAP.DESARROLLO.tenis_bet import ThreadBet

if __name__ == "__main__":
	cola1 = queue.Queue()
	cola2 = queue.Queue()
	cola3 = queue.Queue()

	betFair = ThreadBetFair(cola1, cola2)
	bet = ThreadBet(cola1, cola2)

	betFair.start()
	bet.start()