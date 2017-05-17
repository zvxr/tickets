
import ticketer

from setuptools import setup, find_packages


setup(
    name = "ticketer",
    version = ticketer.__version__,
    author = "Mike McConnell",
    author_email = "djrahl84@gmail.com",
    description = ("HTTP service that facilitates issuing and redeeming tickets."),
    keywords = "pulselocker",
    url = "https://github.com/zvxr/ticketer",
    packages=find_packages(),
)
