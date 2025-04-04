from setuptools import find_packages
from setuptools import setup


_config = {
    "name": "lumao-utils",
    "url": "",
    "author": "Maginaro",
    "author_email": "",
    "packages": find_packages(),
    "classifiers": [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Independent",
    ],
    "python_requires": ">=3.7",
    "install_requires": [
        "web3>=6.0.0",
        "termcolor==1.1.0",
        "eth-account==0.8.0",
        "cryptography>=36.0.1",
        "requests==2.25.1",
        "solana>=0.31.0",
        "solders>=0.19.0",
    ]
}


def main() -> int:
    setup(**_config)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
