from setuptools import find_packages, setup


__VERSION__ = '0.0.1'


setup_requires = [
    'pytest-runner',
]


# package requirements
install_requires = [
    'aiohttp==3.3.2',
    'aiovk==2.2.1'
]


tests_require = [
    'asynctest',
    'mypy',
    'pytest',
    'pytest-aiohttp',
    'pytest-cov',
    'pytest-flake8',
    'pytest-mock',
    'pytest-mypy',
    'pytest-sugar',
]


# entry points
console_scripts:list = []


dependency_links:list = []


setup(
    name='lina_community_edition',
    version=__VERSION__,
    description='Lina VK Dicebot Community Edition',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: AsyncIO',
        'Natural Language :: Russian',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.7',
        'Topic :: Communications',
        'Topic :: Communications :: Chat',
    ],
    zip_safe=False,
    packages=find_packages(exclude=['tests']),
    entry_points={'console_scripts': console_scripts},
    python_requires='>=3.7',
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    dependency_links=dependency_links,
)
