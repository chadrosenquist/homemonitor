from setuptools import setup

import homemonitor.version

setup(
    name='homemonitor',
    version=homemonitor.version.__version__,
    description='Provides a way to monitor your home with your Raspberry Pi.',
    author='Chad Rosenquist',
    author_email='chadrosenquist@gmail.com',
    url='https://github.com/chadrosenquist/homemonitor',
    packages=['homemonitor'],
    license='MIT'
)
