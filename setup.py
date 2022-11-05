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
        "web3==5.31.1",
        "termcolor==1.1.0",
        "eth-account==0.5.9",
        "eth-abi==2.1.1",
        "cryptography==36.0.2",
        "requests==2.25.1"
    ]
}


def main() -> int:
    setup(**_config)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
