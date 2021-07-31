
from distutils.core import setup

setup(
    name='chessplot',
    version='1.0',
    license="GPLv3.0",
    description="Package for visualising chess games",
    author="Timothy May",
    url="https://github.com/tmay-sarsaparilla/PGNParser",
    download_url="https://github.com/tmay-sarsaparilla/PGNParser/archive/refs/tags/v1.0-beta.tar.gz",
    keywords=["chess", "pgn", "visualisation", "parser", "gif", "pdf"],
    packages=["chessplot"],
    python_requires=">=3.7",
    install_requires=["numpy>=1.21.1", "Pillow>=8.3.1"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Board Games",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7"
    ]
)
