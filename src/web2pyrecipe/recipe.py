# -*- coding: utf-8 -*-
from subprocess import call
import os
from zipfile import ZipFile
from tarfile import TarFile
from zc.buildout.easy_install import script_header, _safe_arg
from zc.recipe.egg.egg import Eggs
import zc.recipe.egg
import shutil
import logging
from zc.buildout import UserError
import sys 
from web2pyrecipe.template import script_templates

"""
A recipe for installing the lastest web2py framework version and all the apps in
the 'appdir' options. It defines the 'default' option as the default web2py's app.
"""

FOLDER = os.path.abspath(os.path.dirname(__file__))

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.script_name = options.get('script-name', self.name)
        self.target = options.get('target', '')
        self.app_fabric = options.get('app_fabric', '')
        self.web2py_folder = os.path.join(self.buildout['buildout']['webroot-directory'], 'web2py')
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)

    def install(self):
        """Installer"""
        source = self.options.get('source')
        default_app = self.options.get('project') or 'welcome'
            
        if os.path.exists(self.web2py_folder):
            shutil.rmtree(self.web2py_folder)
        self._untar(source, self.web2py_folder)

        self._install_app(default_app)

        self._set_default_app(default_app)
        script_paths = []

        extra_paths = self.get_extra_paths()
        requirements, ws = self.egg.working_set(['web2pyrecipe'])
        # Make the wsgi and fastcgi scripts if enabled
        script_paths.extend(self.make_scripts(extra_paths, ws))
        return script_paths

    def _install_app(self, app_name):
        os.symlink(os.path.join(self.buildout['buildout']['directory'], app_name), 
                os.path.join(self.web2py_folder, 'applications', app_name))

    def _set_default_app(self, default_app):
        routes = open(os.path.join(self.web2py_folder, 'routes.py'), 'w+')
        routes.write("default_application = '%s'\n" % default_app + \
                     "default_controller = 'default'\n" + \
                     "default_function = 'index'\n"
                     )
        routes.close()

    def _untar(self, archive, destination):
        tar = TarFile.open(archive)
        tar.extractall(path=destination)

    def make_scripts(self, extra_paths, ws):
        scripts = []
        _script_template = zc.buildout.easy_install.script_template
        for protocol in ('wsgi', 'web2py'):
            zc.buildout.easy_install.script_template = script_templates.get(protocol)
            if self.options.get(protocol, '').lower() == 'true':
                project = self.options.get('projectegg',
                                           self.options['project'])
                scripts.extend(
                    zc.buildout.easy_install.scripts(
                        [('%s.py' % protocol,
                          'web2pyrecipe.%s' % protocol, 'main')],
                        ws,
                        self.options['executable'],
                        self.web2py_folder,
                        extra_paths=extra_paths,
                        arguments="'%s', logfile='%s'" % (
                            project,
                            self.options.get('logfile')),
                        initialization=f"path = {self.web2py_folder}"))
        zc.buildout.easy_install.script_template = _script_template
        return scripts

    def get_extra_paths(self):
        extra_paths = [self.buildout['buildout']['directory']]

        # Add libraries found by a site .pth files to our extra-paths.
        if 'pth-files' in self.options:
            import site
            for pth_file in self.options['pth-files'].splitlines():
                pth_libs = site.addsitedir(pth_file, set())
                if not pth_libs:
                    self.log.warning(
                        "No site *.pth libraries found for pth_file=%s" % (
                         pth_file,))
                else:
                    self.log.info("Adding *.pth libraries=%s" % pth_libs)
                    self.options['extra-paths'] += '\n' + '\n'.join(pth_libs)

        pythonpath = [p.replace('/', os.path.sep) for p in
                      self.options['extra-paths'].splitlines() if p.strip()]

        extra_paths.extend(pythonpath)
        return extra_paths

    def update(self):
        extra_paths = self.get_extra_paths()
        requirements, ws = self.egg.working_set(['web2pyrecipe'])
        # Make the wsgi and fastcgi scripts if enabled
        self.make_scripts(extra_paths, ws)
