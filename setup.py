from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lupusecio',
    version='0.0.1',
    description='LupusecIO is a tool to control a XT1 and XT2 alarm panel',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/maegar/lupusec',
    author='Paul Proske',
    author_email='proske.paul@googlemail.com',
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Home Automation',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='lupusec xt1 xt2 home automation',
    packages=find_packages(),
    python_requires='>=3.4, <4',
    install_requires=['demjson', 'requests'],  # Optional
    entry_points = {
        'console_scripts': [
            'lupusecio=lupusecio.__main__:main',
        ],
    },
    project_urls = {
        'Bug Reports': 'https://github.com/Maegar/lupusec/issues',
        'Funding': 'https://www.buymeacoffee.com/Maegar',
        'Source': 'https://github.com/Maegar/lupusec',
    },
)