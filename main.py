import click
from db.models import Group, Account, Tag
from src.totp import Totp
from src.secret import Secret
from datetime import timezone, datetime

import time
from rich.progress import Progress, BarColumn, TimeRemainingColumn
from rich.console import Console
from rich.table import Table


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
@click.argument("service")
@click.argument("seed")
@click.argument("name", default="")
@click.option("-t", "--tag", default=[], help="tags applied to apply", multiple=True)
def add(service, seed, name, tag):
    group, _ = Group.objects.get_or_create(name="work")
    click.echo(f"Adding {service}, {seed}, {name}")

    account = Account.objects.create(service=service, seed=seed, name=name, group=group)

    if tag:
        for t in tag:
            tag_object = Tag.objects.create(group=group, name=t)
            tag_object.account.add(account)


@cli.command()
@click.argument("id")
def remove(id):
    group, _ = Group.objects.get_or_create(name="work")
    account = group.account_set.get(id=id)

    click.echo(f"Removing {account.service}: {account.name}")

    account.delete()


@cli.command()
@click.argument("id")
def code(id):
    group, _ = Group.objects.get_or_create(name="work")
    account = group.account_set.get(id=id)

    totp = Totp(Secret.from_base32(account.seed), code_digits=6, algorithm="sha1")

    while 1:
        start = datetime.now(tz=timezone.utc).second % 30
        click.secho(totp.generate_code(), fg="green")
        count_down(start)


@cli.command()
def list():
    table = Table(title="Accounts", show_lines=True)
    table.add_column("ID")
    table.add_column("Service", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Tags")

    accounts = Account.objects.all()

    for account in accounts:
        table.add_row(str(account.id), account.service, account.name, account.tags())

    console = Console()
    console.print(table)


if __name__ == "__main__":
    cli()
