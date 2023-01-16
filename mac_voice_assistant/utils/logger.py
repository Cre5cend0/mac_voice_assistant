import logging

# Create and configure logger
logging.basicConfig(filename="assist.log",
                    format='%(name)s::%(levelname)s::%(asctime)s::%(message)s',
                    filemode='w')

# Creating an object
log = logging.getLogger()

# Setting the threshold of logger to DEBUG
log.setLevel(logging.DEBUG)


