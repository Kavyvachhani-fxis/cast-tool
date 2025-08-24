from setuptools import setup, find_packages

setup(
    name='cast_tool',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'docker',
        'pyyaml',
        'jenkinsapi'
    ],
    entry_points={
        'console_scripts': [
            'cast-tool = cast_tool.install:main',
        ],
    },
)
