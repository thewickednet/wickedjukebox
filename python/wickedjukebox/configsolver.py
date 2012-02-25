from ConfigParser import SafeConfigParser
from os import getenv, pathsep, getcwd
from os.path import expanduser, exists, join
import logging

LOG = logging.getLogger(__name__)
CONF = None

def config(group, app, search_path=None, conf_name=None, force_reload=False):
    """
    Searches for an appropriate config file. If found, return the filename, and
    the parsed search path

    group
        an application group (f. ex.: your company name)

    app
        an application identifier (f.ex.: the application module name)

    search_path
        if specified, set the config search path to the given value. The path
        can use OS specific separators (f.ex.: ":" on posix, ";" on windows) to
        specify multiple folders. These folders will be searched in the
        specified order. The first file found is parsed.

    conf_name
        if specified, this can be used to override the configuration filename
        (default="app.ini")

    force_reload
        if set to true, the config is reloaded, even if it was alrady loaded in
        the application. Default = False
    """
    global CONF

    # only load the config if necessary (or explicitly requested)
    if CONF and not force_reload:
        return CONF

    path_var = "%s_PATH" % app.upper()
    filename_var = "%s_CONFIG" % app.upper()

    # default search path
    path = [getcwd(),
            expanduser('~/.%s/%s' % (group, app)),
            '/etc/%s/%s' % (group, app)]

    # if an environment variable was specified, override the default path
    env_path = getenv(path_var)
    if env_path:
        path = env_path.split(pathsep)

    # If a path was passed directly to this method, override the path again
    if search_path:
        path = search_path.split(pathsep)

    # same logic for the configuration filename. First, try the runtime
    # environment (with a default fallback):
    config_filename = getenv(filename_var, 'app.ini')

    # If a filename was passed directly, override the value
    if conf_name:
        config_filename = conf_name

    # Next, use the resolved path to find the filenames
    detected_conf = None
    for dir in path:
        conf_name = join(dir, config_filename)
        if exists(conf_name):
            detected_conf = conf_name
            break

    parser = SafeConfigParser()
    detected_conf, path = detected_conf, path
    if not detected_conf:
        LOG.warning("No config file named %s found! Search path was %r" % (config_filename, path))
        CONF = parser
        return CONF

    parser.read(detected_conf)
    LOG.info("Loaded settings from %r" % detected_conf)

    CONF = parser
    return CONF
