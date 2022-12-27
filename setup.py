import os

from setuptools import find_packages, setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='mac_voice_assistant',
    version='0.2.7',
    packages=find_packages(),
    package_data={'mac_voice_assistant': ['audio_samples/beep.wav', 'default_intents.json']},
    url='https://pypi.org/project/mac-voice-assistant/',
    author='Manish Raj',
    author_email='manishraj1.618@gmail.com',
    description='A generic voice assistant',
    long_description=read('README.md'),
    keywords="mac voice assistant",
)
