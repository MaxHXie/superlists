from django.db import models

# Create your models here.
class List(models.Model):
    pass

class Item(models.Model):
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)

'''
Deleting migrations is dangerous. We do need to do it now and again, because we don't
always get our models code right on the first go. But if you delete a migration that's already
been applied to a database somewhere, Django will be confused about what state it's in,
and how to apply future migrations.

You should only do it when you're sure the migration hasn't been used.

A good rule of thumb is that you should never delete or modify a migration
that's already been committed to your VCS.
'''
