import click
from db.models import Group, Account, Tag
from .totp import Totp
from .secret import Secret
from datetime import timezone, datetime
from django.core.management import call_command

import time
from rich.progress import Progress, BarColumn, TimeRemainingColumn, TextColumn
from rich.console import Console
from rich.table import Table


def count_down(start, code, time_step):
    with Progress(
        TextColumn(f"[bold green]{code}"),
        BarColumn(),
        TimeRemainingColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("", total=time_step, completed=start)

        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(1)


GroupName = "default"


@click.group()
def cli():
    pass


@cli.command()
def init():
    call_command("migrate", "db")


@cli.command()
@click.argument("service")
@click.argument("seed")
@click.option(
    "-n",
    "--name",
    default="",
    help="Name to differentiate accounts of the same service",
)
@click.option("-t", "--tag", default=[], help="Tags to apply", multiple=True)
def add(service, seed, name, tag):
    group, _ = Group.objects.get_or_create(name=GroupName)
    click.echo(f"Adding {service}:{name}")

    account = Account.objects.create(service=service, seed=seed, name=name, group=group)

    if tag:
        for t in tag:
            tag_object = Tag.objects.get_or_create(group=group, name=t)
            tag_object.account.add(account)


@cli.command()
@click.argument("id")
def remove(id):
    group, _ = Group.objects.get_or_create(name=GroupName)
    account = group.account_set.get(id=id)

    click.echo(f"Removing {account.service}:{account.name}")

    account.delete()


@cli.command()
@click.argument("id")
def code(id):
    group, _ = Group.objects.get_or_create(name=GroupName)
    account = group.account_set.get(id=id)
    time_step = account.period

    totp = Totp(
        Secret.from_base32(account.seed),
        code_digits=6,
        algorithm=account.get_algorithm(),
        time_step=time_step,
    )

    while 1:
        start = datetime.now(tz=timezone.utc).second % time_step
        count_down(start, totp.generate_code(), time_step)


@cli.command()
def list():
    table = Table(title="Accounts", show_lines=True)
    table.add_column("ID")
    table.add_column("Service", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Tags")

    group, _ = Group.objects.get_or_create(name=GroupName)
    accounts = group.account_set.all()

    for account in accounts:
        table.add_row(str(account.id), account.service, account.name, account.tags())

    console = Console()
    console.print(table)


if __name__ == "__main__":
    cli()
