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
from config import PASSWORD_FILE, DB_PATH, GROUP_NAME
import os
from pathlib import Path
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
import binascii


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


def generate_master_password(password, salt):
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=1,
        lanes=4,
        memory_cost=2 * 1024 * 1024,
        ad=None,
        secret=None,
    )

    digest = kdf.derive(password.encode())
    return binascii.hexlify(digest).decode()


@click.group()
def cli():
    pass


@cli.command()
def init():
    if Path(DB_PATH).is_file():
        return

    call_command("migrate", "db")
    Group.objects.get_or_create(name=GROUP_NAME, salt=os.urandom(16))


@cli.command()
def post_init():
    password = click.prompt("Enter a password", type=str)
    group = Group.objects.get(name=GROUP_NAME)

    with open(PASSWORD_FILE, "a") as file:
        master_password = generate_master_password(password=password, salt=group.salt)
        file.write(master_password)


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
    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    click.echo(f"Adding {service}:{name}")

    account = Account.objects.create(service=service, seed=seed, name=name, group=group)

    if tag:
        for t in tag:
            tag_object = Tag.objects.get_or_create(group=group, name=t)
            tag_object.account.add(account)


@cli.command()
@click.argument("id")
def remove(id):
    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    account = group.account_set.get(id=id)

    click.echo(f"Removing {account.service}:{account.name}")

    account.delete()


@cli.command()
@click.argument("id")
def code(id):
    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    account = group.account_set.get(id=id)
    time_step = account.period
    code_length = account.digits

    totp = Totp(
        Secret.from_base32(account.seed),
        code_digits=code_length,
        algorithm=account.get_algorithm(),
        time_step=time_step,
    )

    while 1:
        start = datetime.now(tz=timezone.utc).second % time_step
        code = str(totp.generate_code()).zfill(code_length)
        count_down(start, code, time_step)


@cli.command()
def list():
    table = Table(title="Accounts", show_lines=True)
    table.add_column("ID")
    table.add_column("Service", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Tags")

    group, _ = Group.objects.get_or_create(name=GROUP_NAME)
    accounts = group.account_set.all()

    for account in accounts:
        table.add_row(str(account.id), account.service, account.name, account.tags())

    console = Console()
    console.print(table)


if __name__ == "__main__":
    cli()
