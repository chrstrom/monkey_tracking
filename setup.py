from setuptools import setup, find_packages

setup(
    name='monkey_tracking',
    version='1.0.0',
    author='Christopher Strøm',
    author_email='detoxte@gmail.com',
    description='A package for simulating point objects, useful for testing trackers',
    url='https://github.com/chrstrom/monkey_tracking',
    keywords='point object tracking simulation',
    packages=find_packages(),
    license='MIT',
    python_requires='>=3.6',
)