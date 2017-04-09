import logging
import os
import datetime

current_dir = os.path.dirname(os.path.realpath(__file__))
today = datetime.datetime.today()
today_date = today.strftime("%Y-%m-%d")  # YYYY-MM-DD
today_time = today.strftime("%H%M")  # i.e. 1500

log_file = "{}{}{}{}{} {}.log".format(current_dir,
									os.sep,
									"log_files",
									os.sep,
									today_date,
									today_time)

# Logger that prints to console and file
# from http://stackoverflow.com/a/9321890

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
					# format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
					format="%(message)s",
					datefmt="%m-%d %H:%M",
					filename=log_file,
					filemode="w")
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
# formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
formatter = logging.Formatter("%(message)s")
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger("").addHandler(console)


# Suppress gmusicapi logger
logging.getLogger("gmusicapi.Musicmanager2").setLevel(logging.CRITICAL)

# Suppress other loggers
for key in logging.Logger.manager.loggerDict:
	logging.getLogger(key).setLevel(logging.CRITICAL)

# Initialize project loggers
config_logger = logging.getLogger("BetterMM.config")
main_logger = logging.getLogger("BetterMM.main")
mm_logger = logging.getLogger("BetterMM.mm")