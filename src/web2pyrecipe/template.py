from zc.buildout.easy_install import script_header, _safe_arg

script_templates = {
    "wsgi": script_header + """
%(relative_paths_setup)s
import os
import sys
sys.path[0:0] = [
    %(path)s,
]
%(initialization)s
os.chdir(path)

if not os.path.isdir('applications'):
    raise RuntimeError('Running from the wrong folder')

import gluon.main
application = gluon.main.wsgibase
""",
    "web2py": script_header + """
%(relative_paths_setup)s
import os
import sys
sys.path[0:0] = [
    %(path)s,
]
%(initialization)s
os.chdir(path)

if __name__ == '__main__':
    import gluon.widget
    gluon.widget.start()
"""
}
