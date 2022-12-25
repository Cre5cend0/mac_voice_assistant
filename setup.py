import os

from setuptools import setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='mac_voice_assistant',
    version='0.0.1',
    packages=['mac_voice_assistant', 'tests'],
    url='https://pypi.org/project/mac-voice-assistant/',
    license='MIT',
    author='Manish Raj',
    author_email='manishraj1.618@gmail.com',
    description='A generic voice assistant',
    long_description=read('README'),
    keywords="mac voice assistant",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
