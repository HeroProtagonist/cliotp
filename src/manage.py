import os
from pathlib import Path

DB_ROOT_DIR = Path(os.getenv('CLIOTP_DB_PATH', Path.home()))
DB_DIR = DB_ROOT_DIR.joinpath(".cliotp")

DB_DIR.mkdir(exist_ok=True)

def init_django():
    import django
    from django.conf import settings

    if settings.configured:
        return

    settings.configure(
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        INSTALLED_APPS=[
            "db",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": str(DB_DIR / "cliopt.sqlite3"),
            }
        },
    )
    django.setup()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    init_django()
    execute_from_command_line()
