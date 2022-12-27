import os

from setuptools import find_packages, setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name='mac_voice_assistant',
    version='0.2.3',
    packages=find_packages(),
    py_modules=['IA'],
    url='https://pypi.org/project/mac-voice-assistant/',
    license='MIT',
    author='Manish Raj',
    author_email='manishraj1.618@gmail.com',
    description='A generic voice assistant',
    long_description=read('README.md'),
    keywords="mac voice assistant",
    install_requires=['numpy', 'nltk', 'tensorflow', 'PyAudio', 'playsound', 'pyttsx3', 'SpeechRecognition', 'pyjokes'],
)
