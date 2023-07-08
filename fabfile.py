# type: ignore
from fabric import task


@task
def run(ctx):
    ctx.run("./env/bin/wjb runserver", pty=True, replace_env=False)
