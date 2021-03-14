import os
from setuptools import setup, find_packages

version = '0.0.1'

def read_file(name):
    return open(os.path.join(os.path.dirname(__file__),
                                         name)).read()

readme = read_file('README.md')

setup(name = "web2pyrecipe",
      version=version,
      description="Buildout recipe for web2py",
      long_description=readme,
      package_dir={'': 'src'},
      packages=find_packages('src'),
      keywords='',
      author='Viktor Vraniak',
      author_email='viktor.vraniak@gmail.com',
      url='https://github.com/tyctor/web2pyrecipe',
      license='BSD',
      zip_safe=False,
      install_requires=[
        'zc.buildout',
        'zc.recipe.egg',
#        'web2py',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      default = web2pyrecipe.recipe:Recipe
      """,
      )

