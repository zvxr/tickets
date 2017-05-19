
import tickets

from setuptools import setup, find_packages


setup(
    name = "tickets",
    version = tickets.__version__,
    author = "Mike McConnell",
    author_email = "djrahl84@gmail.com",
    description = ("HTTP service that facilitates issuing and redeeming tickets."),
    url = "https://github.com/zvxr/tickets",
    packages=find_packages(),
)
