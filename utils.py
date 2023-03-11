import coloredlogs
import logging
import datetime
from models import UserData

import random
import string

import json
import configparser
config = configparser.ConfigParser()
config.read('bot.ini')


logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)


def get_and_updateUser(user_id, name):
    print("--getting user!")
    logger.debug(f"getting user '{user_id}' !")

    if UserData.select().where(
        UserData.user_id == user_id
    ).exists() == True:

        user = UserData.get(user_id=user_id)
        try:
            user.set_name(name)
        except:
            pass

    else:
        while True:
            try:
                user = UserData.create(
                    name=name, user_id=user_id
                )
                print("--User created!")
                break

            except Exception as e:
                print(e)
                pass

    return user


def randStr(chars=string.ascii_uppercase + string.digits + string.ascii_lowercase, N=5):
    return ''.join(random.choice(chars) for _ in range(N))

