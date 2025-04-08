# setup.py
from setuptools import setup, find_packages

setup(
    name='honeygotchi',
    version='0.1.0',
    description='Smart adaptive honeypot with personality, inspired by Pwnagotchi.',
    author='YourName',
    author_email='you@example.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Add Python deps if needed, e.g.
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'honeygotchi=main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
    ],
    python_requires='>=3.7',
)