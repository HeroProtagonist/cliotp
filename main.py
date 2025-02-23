import click
from src.totp import Totp
from datetime import timezone, datetime

import time
from rich.progress import Progress, BarColumn, TimeRemainingColumn


def count_down(start):
    with Progress(BarColumn(), TimeRemainingColumn()) as progress:
        task = progress.add_task("", total=30, completed=start)

        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(1)


@click.group()
def cli():
    pass


@cli.command()
def add():
    click.echo("Adding")


@cli.command()
def remove():
    click.echo("Removing")


@cli.command()
def code():
    totp = Totp("foo", code_digits=6)

    while 1:
        start = datetime.now(tz=timezone.utc).second % 30
        click.secho(totp.generate_code(), fg="green")
        count_down(start)


if __name__ == "__main__":
    cli()
