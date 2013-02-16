from django.db import models
from django.utils.translation import ugettext_lazy as _

# We'll be using django auth. Applications in the project should
# import it from here and not from django.contrib.auth.
from django.contrib.auth.models import User, Group


class Trait(models.Model):
    """
    Represents a trait of a `Worker` that can affect his ability to
    perform chores of certain `ChoreType`s.

    Who is assigned `Allocation`s of a `ChoreType`? All `Worker`s who
    are allowed to perform it.

    e.g. for a certain chore this may be all men below the age of 23
    who hold managerial positions and aren't forbidden by a doctor to
    do physical work.

    This is represented by traits: A `Worker` who has the `male`,
    `below 23` and `manager` traits and doesn't have the `forbidden to
    do physical work` will be assigned the Chore.
    """
    name = models.CharField(max_length=100)
    # If None, this trait is managed automatically by code. Else,
    # members of the group are allowed to change `Worker`s' trait
    # status for this trait.

    # TODO: supervisor_group = models.ForeignKey(Group, null=True, blank=True)

    class Meta:
        verbose_name = _('Trait')
        verbose_name_plural = _('Traits')

    def __unicode__(self):
        return self.name


class Body(models.Model):
    """
    Represents an entity capable of being assigned `Allocation`s,
    trading them and maybe assigning them.
    """
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("Organization", null=True, blank=True)

    class Meta:
        verbose_name = _('Body')
        verbose_name_plural = _('Bodies')

    def __unicode__(self):
        return self.name


class Organization(Body):
    """
    Represents an organization or sub-organization that has people
    (`managers`) responsible for managing its `Allocation`s.
    """
    managers = models.OneToOneField(Group)

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')


class Worker(Body):
    """
    Represents a single person capable of performing chores, will
    probably be assigned `Allocation`s and might trade them or perform
    them himself.
    """
    user = models.OneToOneField(User)
    traits = models.ManyToManyField(Trait)

    class Meta:
        verbose_name = _('Worker')
        verbose_name_plural = _('Workers')
