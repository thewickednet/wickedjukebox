import json
from os import getuid
from os.path import abspath
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict

from invoke import task


def get_db_port(json_doc: str) -> int:

    data = json.loads(json_doc)
    ports = data[0]["NetworkSettings"]["Ports"]["3306/tcp"]
    port_numbers = {int(info["HostPort"]) for info in ports}
    assert len(port_numbers) == 1
    return port_numbers.pop()


def reconfigure(
    ctx, template: Path, target: Path, variables: Dict[str, str]
) -> None:
    if not template.is_file():
        raise ValueError("%s should be a regular file!" % template)
    if target.exists() and not target.is_file():
        raise ValueError("%s should be a regular file!" % target)

    if target.exists():
        # Instead of using the application template, we will use the existing
        # file to edit
        template = target

    template_str = template.read_text()

    for key, value in variables.items():
        template_str = template_str.replace("{{%s}}" % key, value)

    with NamedTemporaryFile() as tmpfile:
        tmpfile.write(template_str.encode("utf8"))
        tmpfile.flush()

        ctx.run("$EDITOR %s" % tmpfile.name, pty=True, replace_env=False)
        diff = ctx.run(
            "diff %s %s" % (tmpfile.name, template), warn=True, hide=True
        )

        if diff.exited == 0:
            # no changes to file. we can return with no-op
            print("No changes made. Keeping old file.")
            return

        print("Applying changes %s -> %s" % (template, target))
        ctx.run("mkdir -p %s" % target.parent)
        ctx.run("cp -v %s %s" % (tmpfile.name, target))


@task
def develop(ctx):
    ctx.run("[ -d env ] || python3 -m venv env")
    ctx.run("./env/bin/pip install -U pip")
    ctx.run("./env/bin/pip install -e .[dev,test]")
    print("Running DB container...")
    ctx.run("./db_container.sh", warn=True, pty=True)
    output = ctx.run("docker inspect jukeboxdb", hide="both")
    db_port = get_db_port(output.stdout)
    print("The following config-file needs the MySQL port you see above!")
    input("Press ENTER to continue...")
    reconfigure(
        ctx,
        Path("alembic.ini.dist"),
        Path("alembic.ini"),
        variables={"db_port": str(db_port)},
    )
    reconfigure(
        ctx,
        Path("config.ini.dist"),
        Path(".wicked/wickedjukebox/config.ini"),
        variables={"db_port": str(db_port)},
    )
    ctx.run("./env/bin/alembic upgrade head")


@task
def test(ctx, autorun=False, cover=False, lf=False):
    from configparser import ConfigParser

    cfg = ConfigParser()
    cfg.read(".wicked/wickedjukebox/config.ini")
    dsn = cfg.get("database", "dsn")

    if autorun:
        base_cmd = 'git ls-files | entr -c sh -c "%s"'
    else:
        base_cmd = "%s"

    runner_cmd = ["./env/bin/pytest --sqlalchemy-connect-url=%s" % dsn]

    if lf:
        runner_cmd.append("--lf")

    if cover:
        runner_cmd.append(
            "--cov-report=term-missing "
            "--cov-report=xml:coverage.xml "
            "--cov wickedjukebox "
        )

    runner_cmd = " ".join(runner_cmd)
    ctx.run(base_cmd % runner_cmd, pty=True, replace_env=False)


@task
def build_mpd(ctx):
    """
    Builds a docker-image for mpd
    """
    ctx.run("docker build -t wickedjukebox/mpd .", pty=True)


@task
def run_mpd(ctx, mp3_path=""):
    """
    Runs MPD in an ephemeral docker-container

    This is mainly intended for testing. For real production use, a persistent
    volume should be used for ``/var/lib/mpd``
    """
    build_mpd(ctx)
    uid = getuid()
    volume = ""
    if mp3_path:
        volume = f"--volume={abspath(mp3_path)}:/var/lib/mpd/music:ro "
    ctx.run(
        "docker run --rm "
        f"--volume=/run/user/{uid}/pulse:/run/user/{uid}/pulse {volume} "
        "--name wickedjukebox_mpd "
        "wickedjukebox/mpd",
        pty=True,
    )
