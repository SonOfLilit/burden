from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from hr.models import User, Body
from design.models import ChoreType


class SoftDeleteManager(models.Manager):
    """
    See `DeactivableModel`.
    """
    def get_query_set(self):
        return super(SoftDeleteManager, self).get_query_set().filter(deleted=False)

    def all_with_deleted(self):
        return super(SoftDeleteManager, self).get_query_set()

    def deleted_set(self):
        return super(SoftDeleteManager, self).get_query_set().filter(deleted=True)


class DeactivableModel(models.Model):
    """
    Model that supports "soft-delete" of rows, meaning they will
    not show up in `Model.objects.all()` but /will/ show up in
    `Models.all_objects.all()`.

    See: http://codespatter.com/2009/07/01/django-model-manager-soft-delete-how-to-customize-admin/
    """
    deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None):
        # to support multiple DBs, accept the using parameter and do
        # something useful with it
        self.deleted = True
        self.save()


class DeactivableNonEditableModel(DeactivableModel):
    """
    `DeactivableModel` that only supports creating and deleting rows, not
    any other form of editing.

    Doesn't promise to be airtight, but still very useful to catch bugs.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk:
            if self.deleted:
                kwargs["update_fields"] = ["deleted"]
                return super(
                    DeactivableNonEditableModel, self).save(*args, **kwargs)
            else:
                raise IntegrityError()
        else:
            return super(
                DeactivableNonEditableModel, self).save(*args, **kwargs)


class Allocation(DeactivableNonEditableModel):
    """
    Represents an instance of a `ChoreType` that has a date and length
    and needs to be assigned to a `Body`.
    """
    chore = models.ForeignKey(ChoreType)
    date = models.DateField()
    days = models.IntegerField()
    # TODO: current_performer, assignment_chain, can_take, take, assign, trade

    class Meta:
        verbose_name = _("Allocation")
        verbose_name_plural = _("Allocations")

    def __unicode__(self):
        return u"%d days of %s starting %s" % (
            self.days, self.chore, self.date)


class Assignment(DeactivableNonEditableModel):
    """
    Represents an edge in the graph of `Allocation` assignments and
    trade - either an assignment or a trade (which behave very
    similarly).

    When an `Allocation` is created, it is assigned from `None` to its
    `ChoreType`'s `owners`.

    When a `Body` is the current performer of an `Allocation`
    (i.e. there are more active `Assignment`s of the `Allocation` to
    the `Body` than from the `Body`), it may assign it to a child or
    trade it to any other `Body`.

    If there is a direct path of `Assignment`s of an `Allocation` from
    a `Body` to its current performer (always from parent to child,
    never a trade), it may unassign it from all its descendants,
    rendering those `Assignment`s inactive and thus becoming once
    again the performer of the `Allocation`. This is usually done in
    order to immediately assign it elsewhere or trade it.

    Notice how trading an `Assignment` prevents it from being
    reassigned in the future by the ancestors of neither the giving
    party nor the taking party. This is good and by design and is
    meant to protect the sanity of the system, specifically the
    principles stating:

    * A `Body` can't affect an `Allocation` that doesn't belong to it
      (even if its child is the current performer)

    * Once a `Body` trades something away it won't be troubled by it
      again.
    """
    allocation = models.ForeignKey(Allocation)
    # TODO: figure out wether we need these related_name-s and how to call them
    old_performer = models.ForeignKey(Body, related_name="+")
    new_performer = models.ForeignKey(Body, related_name="+")
    is_trade = models.BooleanField()
    # see below documentation of `Transaction`
    transaction = models.ForeignKey("Transaction")

    class Meta:
        verbose_name = _("Assignment")
        verbose_name_plural = _("Assignments")

    def __unicode__(self):
        maybe_deleted = "DELETED " if self.deleted else ""
        return u"%s: %s%s >-%s-> %s" % (
            self.transaction.timestamp,  # pylint: disable-msg=E1101
            maybe_deleted,
            self.old_performer,
            self.allocation,
            self.new_performer)


class Transaction(DeactivableNonEditableModel):
    """Represents a bunch of `Assignment`s done together, e.g. a trade or
    an organization assigning `Allocation`s to sub-organizations.

    Every `Assignment` is part of a `Transaction` (though perhaps a
    trivial one).
    """
    timestamp = models.DateField(auto_now_add=True)
    # if there were authorities who authorized this transaction, they
    # are recorded here
    signers = models.ManyToManyField(User)
    # TODO: Do we need to enumerate participating parties? What if one
    # is assigning to many?

    # TODO: Do we need is_trade? Should it be only here for
    # normalization despite being needed so often?  Maybe here it
    # should be a property reading from assignments[0]?
