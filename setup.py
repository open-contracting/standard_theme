# -*- coding: utf-8 -*-
"""`sphinx_rtd_theme` lives on `Github`_.

.. _github: https://www.github.com/snide/sphinx_rtd_theme

"""
from setuptools import setup


setup(
    name='standard_theme',
    url='https://github.com/open-contracting/standard_theme/',
    description='Derived from ReadTheDocs.org theme for Sphinx, 2013 version.',
    long_description=open('README.rst').read(),
    zip_safe=False,
    packages=['standard_theme'],
    package_data={'standard_theme': [
        'theme.conf',
        '*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/font/*.*'
    ]},
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
)
