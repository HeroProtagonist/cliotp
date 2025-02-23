import click
from db.models import Group, Account
from src.totp import Totp
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
def add(service, seed, name):
    group, _ = Group.objects.get_or_create(name="work")
    print(group)
    click.echo(f"Adding #{service}, #{seed}, #{name}")
    Account.objects.create(service=service, seed=seed, name=name, group=group)


@cli.command()
def remove():
    click.echo("Removing")


@cli.command()
@click.argument("id")
def code(id):
    group, _ = Group.objects.get_or_create(name="work")
    account = group.account_set.get(id=id)
    totp = Totp(account.seed, code_digits=6)

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

    accounts = Account.objects.all()

    for account in accounts:
        table.add_row(str(account.id), account.service, account.name)

    console = Console()
    console.print(table)


if __name__ == "__main__":
    cli()
