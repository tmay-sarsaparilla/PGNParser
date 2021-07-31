
from setuptools import setup, find_packages

setup(
    name='chessplot',
    version='1.0',
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=["numpy>=1.21.1", "Pillow>=8.3.1"]
)
