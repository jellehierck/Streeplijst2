from setuptools import setup, find_packages

setup(
        name='Streeplijst2',
        version='2.0.0',
        url='',
        license='',
        author='Jelle Hierck',
        author_email='jelle.hierck@gmail.com',
        description='Paradoks Streeplijst',
        packages=find_packages(include=['streeplijst', 'streeplijst.*']),
        install_requires=[
                'requests'
        ],
)
