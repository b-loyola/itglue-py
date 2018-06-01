from setuptools import setup

setup(
    name='itglue',
    version='0.1.0',
    description='A simple wrapper for the IT Glue API',
    url='http://github.com/bloyola/itglue-py',
    author='Ben Loyola',
    author_email='bloyola@itglue.com',
    license='MIT',
    packages=['itglue'],
    install_requires=['requests'],
    zip_safe=False
)
