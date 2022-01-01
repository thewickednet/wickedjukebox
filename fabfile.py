import json
import re
from os import getuid
from os.path import abspath
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import sleep
from typing import Dict

from invoke import task


def get_db_port(json_doc: str) -> int:

    data = json.loads(json_doc)
    ports = data[0]["NetworkSettings"]["Ports"]["3306/tcp"]
    port_numbers = {int(info["HostPort"]) for info in ports}
    assert len(port_numbers) == 1
    return port_numbers.pop()


def reconfigure(
    ctx,
    template: Path,
    target: Path,
    variables: Dict[str, str],
    unattended: bool,
) -> None:
    if not template.is_file():
        raise ValueError("%s should be a regular file!" % template)
    if target.exists() and not target.is_file():
        raise ValueError("%s should be a regular file!" % target)

    template_str = template.read_text()

    for key, value in variables.items():
        template_str = template_str.replace("{{%s}}" % key, value)

    with NamedTemporaryFile(
        prefix=f"{template.name}-to-{target.name}-"
    ) as tmpfile:
        tmpfile.write(template_str.encode("utf8"))
        tmpfile.flush()

        if not unattended:
            ctx.run("$EDITOR %s" % tmpfile.name, pty=True, replace_env=False)

        diff = ctx.run(
            "diff %s %s" % (tmpfile.name, template), warn=True, hide=True
        )

        if diff.exited == 0:
            # no changes to file. we can return with no-op
            print("No changes made. Keeping old file %r." % target)
            return

        print("Applying changes %s -> %s" % (template, target))
        ctx.run("mkdir -p %s" % target.parent)
        do_copy = True
        if target.exists():
            if unattended:
                print(f"{target} exists. Will not overwrite!")
                do_copy = False
            else:
                diff_check = ctx.run(
                    f"diff {tmpfile.name} {target.absolute()}",
                    warn=True,
                    hide="both",
                )
                if diff_check.failed:
                    print(
                        f"!! Local modifications to {target} detected. "
                        "Opening difftool with template and local file"
                    )
                    input("(press Enter to continue)")
                    ctx.run(
                        f"vim -d {tmpfile.name} {target.absolute()}",
                        pty=True,
                        replace_env=False,
                    )
        if do_copy:
            ctx.run("cp -v %s %s" % (tmpfile.name, target))


@task
def run_db_container(ctx):
    """
    Starts a new db-container and adapts ports in config-files if
    necessary.
    """

    container_check = ctx.run(
        "docker inspect jukeboxdb", hide="both", warn=True
    )
    if container_check.failed:
        print("Running DB container...")
        ctx.run("bash db_container.sh", pty=True)
        sleep(10)
        container_check = ctx.run("docker inspect jukeboxdb", hide="both")

    db_port = get_db_port(container_check.stdout)
    reconfigure(
        ctx,
        Path("alembic.ini.dist"),
        Path("alembic.ini"),
        variables={"db_port": str(db_port)},
        unattended=False,
    )
    reconfigure(
        ctx,
        Path("config.ini.dist"),
        Path(".wicked/wickedjukebox/config.ini"),
        variables={"db_port": str(db_port)},
        unattended=False,
    )
    ctx.run("./env/bin/alembic upgrade head")


@task
def develop(ctx):
    ctx.run("[ -d env ] || python3 -m venv env")
    ctx.run("./env/bin/pip install -U pip")
    ctx.run("./env/bin/pip install -e .[dev,test]")
    run_db_container(ctx)
    ctx.run("pre-commit install")


@task
def test(ctx, autorun=False, cover=False, lf=False):
    from configparser import ConfigParser

    run_db_container(ctx)

    cfg = ConfigParser()
    cfg.read(".wicked/wickedjukebox/config.ini")
    dsn = cfg.get("core", "dsn")

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
def run_mpd(ctx, mp3_path, port=6600):
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
        f"-p {port}:6600 "
        "wickedjukebox/mpd",
        pty=True,
    )
