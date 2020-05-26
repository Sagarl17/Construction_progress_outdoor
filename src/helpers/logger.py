import sys
import logging
import datetime
from src.helpers import utils


#       Creating a Custom Logger for logging the process                    #

def setup_custom_logger(name):
	class ContextFilter(logging.Filter):
		def filter(self, record):
			record.memcalc = utils.memcalc()
			record.cpucalc = utils.cpucalc()
			return True



	formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(memcalc)s %(cpucalc)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )

	handler = logging.FileHandler('./logs/lOG_'+str(datetime.datetime.now()) +'.txt', mode='w')
	handler.setFormatter(formatter)
	screen_handler = logging.StreamHandler(stream=sys.stdout)
	screen_handler.setFormatter(formatter)
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)
	logger.addHandler(handler)
	logger.addHandler(screen_handler)
	logger.addFilter(ContextFilter())
	return logger
