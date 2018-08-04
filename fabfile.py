from pathlib import Path
from tempfile import NamedTemporaryFile

from config_resolver import Config
from invoke import run, task


def reconfigure(template: Path, target: Path) -> None:
    if not template.is_file():
        raise ValueError('%s should be a regular file!' % template)
    if target.exists() and not target.is_file():
        raise ValueError('%s should be a regular file!' % target)

    if target.exists():
        # Instead of using the application template, we will use the existing
        # file to edit
        template = target

    with NamedTemporaryFile() as tmpfile:
        run('cat %s > %s' % (template, tmpfile.name))
        run('$EDITOR %s' % tmpfile.name, pty=True)
        diff = run('diff %s %s' % (tmpfile.name, template), warn=True,
                   hide=True)

        if diff.exited == 0:
            # no changes to file. we can return with no-op
            print('No changes made. Keeping old file.')
            return

        print('Applying changes %s -> %s' % (template, target))
        run('mkdir -p %s' % target.parent)
        run('cp -v %s %s' % (tmpfile.name, target))


@task
def develop(unused_ctx):
    run('pipenv install -d -e .')
    run('./db_container.sh', warn=True)
    print('The following config-file needs the MySQL port you see above!')
    input('Press ENTER to continue...')
    reconfigure(
        Path('alembic.ini.dist'),
        Path('alembic.ini'))
    reconfigure(
        Path('config.ini.dist'),
        Path('.wicked/wickedjukebox/config.ini'))
    print('Running DB container...')
    run('alembic upgrade head')


@task
def test(unused_ctx, autorun=False, cover=False):
    cfg = Config('wicked', 'wickedjukebox', require_load=True,
                 filename='config.ini')
    dsn = cfg.get('database', 'dsn')

    if autorun:
        base_cmd = 'find test wickedjukebox -name "*.py" | entr -c sh -c "%s"'
    else:
        base_cmd = '%s'

    runner_cmd = ['pytest --sqlalchemy-connect-url=%s' % dsn]

    if cover:
        runner_cmd.append('--cov-report=term-missing --cov wickedjukebox')

    runner_cmd = ' '.join(runner_cmd)
    run(base_cmd % runner_cmd, pty=True)
