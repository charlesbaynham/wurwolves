import re

import setuptools


setuptools.setup(
    name="backend",
    version="0.0.1",
    author="Charles Baynham",
    author_email="charles.baynham@gmail.com",
    description="Backend for wurwolves",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        r
        for r in open("requirements.in").read().splitlines()
        if r and not re.match(r"\s*\#", r[0])
    ],
    extras_require={
        "dev": [
            r
            for r in open("requirementsDev.in").read().splitlines()
            if r and not re.match(r"\s*\#", r[0])
        ],
    },
)
