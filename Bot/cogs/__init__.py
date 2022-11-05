# Hier kommen alle imports rein die oft gebraucht werden, somit können wir sie einfach alle auf einmal importieren
from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    TYPE_CHECKING
)

import os
import sys
import asyncio
import logging

# debugging
# from color_pprint import cprint

import discord
from discord.ext import commands
from discord import *

Bot = commands.Bot


def log_init(__file__: str) -> logging.Logger:
    filename = __file__.replace('\\', '/').split("/")[-1][:-3]
    return logging.getLogger(f'Extension {filename}')