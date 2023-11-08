import argparse

import discord


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dev", action="store_true", help="use dev environment")
    return parser.parse_args()

def get_user_name(user: discord.User):
    if user.global_name is not None:
        return user.global_name
    elif user.nick is not None:
        return user.nick
    else:
        return user.name
