import os

from setuptools import find_packages, setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='mac_voice_assistant',
    version='0.1.0',
    packages=find_packages(),
    url='https://pypi.org/project/mac-voice-assistant/',
    license='MIT',
    author='Manish Raj',
    author_email='manishraj1.618@gmail.com',
    description='A generic voice assistant',
    long_description=read('README.md'),
    keywords="mac voice assistant",
    install_requires=['numpy', 'nltk', 'tensorflow'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
