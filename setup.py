from setuptools import setup

setup(
    name='envs',
    version='0.1.0',
    packages=['envs'],
    entry_points={
        'console_scripts': [
            'envs = envs.__main__:main'
        ]
    },
)
