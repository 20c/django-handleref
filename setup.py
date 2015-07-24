from setuptools import setup

version = open('config/VERSION').read().strip()
requirements = open('config/requirements.txt').read().split("\n")

setup(
    name='django-handleref',
    version=version,
    author='Twentieth Century',
    author_email='code@20c.com',
    description='track when an object was created or changed and allowe querying based on time and versioning',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[
      'django_handleref', 
      'django_handleref.rest'
    ],
    url = 'https://github.com/20c/django-handleref',
    download_url = 'https://github.com/20c/django-handleref/%s'%version,
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False
)
