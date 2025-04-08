from setuptools import setup, find_packages

with open("requirements.txt") as req:
    required = [line.strip() for line in req if line.strip()]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="honeygotchi",
    version="0.1.0",
    description="[^_^] Your network's cutest trap. Smart. Sneaky. Self-improving.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="hellybrine",
    url="https://github.com/hellybrine/honeygotchi",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    entry_points={
        "console_scripts": [
            "honeygotchi=main:main"
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="honeypot, security, pwnagotchi, raspberrypi, wifi, cybersec, bot",
    python_requires=">=3.7",
)