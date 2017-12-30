
import tickets

from setuptools import setup, find_packages


setup(
    name="tickets",
    version=tickets.__version__,
    author="Mike McConnell",
    author_email="djrahl84@gmail.com",
    description=("HTTP service. "
        "Facilitates issuing and redeeming unique keys."),
    url="https://github.com/zvxr/tickets",
    packages=find_packages(),
)
