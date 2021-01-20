import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='someip', # Replace with your own username
    version='0.0.1',
    author='Florian Münchbach',
    author_email='',
    description='Python library for serializing SOME/IP message payloads',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/FlorianMuenchbach/pysomeiptlv',
    packages=setuptools.find_packages(),
    license='BSD',
    install_requires=[
        # Currently not used:        'backports.cached_property; python_version < '3.8'',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': ['someip-tlv-serializer=someip.tlv.tools.someip_tlv_serializer:main'],
    }
)
