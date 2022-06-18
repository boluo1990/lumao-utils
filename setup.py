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
}


def main() -> int:
    setup(**_config)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
