import csv

from crypto import Crypto


class Mover:
    def __init__(self, group, filename=""):
        self.group = group
        self.accounts = group.account_set.all()
        self.filename = filename or "cliotp_export"

    def export(self):
        with open(f"{self.filename}.csv", "w", newline="") as csvfile:
            fieldnames = ["service", "seed", "name"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            failures = []
            for account in self.accounts:
                try:
                    writer.writerow(
                        self._row(
                            service=account.service,
                            name=account.name,
                            seed=account.seed,
                        )
                    )
                except TypeError as error:
                    failures.append((account.id, error))

            return failures

    def import_file(self):
        with open(f"{self.filename}.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                row["initialization_vector"] = Crypto.random_bytes()
                self.group.account_set.create(**row)

    def _row(self, service, name, seed):
        return {"service": service, "name": name, "seed": seed}
