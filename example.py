from random import randint
import datetime
now = datetime.datetime.now()


def print_data():

    x = str("{}.{}.{}  {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))

    return x


def generate_random_number():
    x = randint(0, 10)
    return x