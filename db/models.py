from django.db import models
from manage import init_django

init_django()


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Group(BaseModel):
    name = models.CharField(max_length=200)


class Account(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    service = models.CharField(max_length=200)
    seed = models.CharField(max_length=256)

    def tags(self):
        account_tags = self.tag_set.all()
        return ", ".join([tag.name for tag in account_tags])


class Tag(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    account = models.ManyToManyField(Account)
    name = models.CharField(max_length=200)
