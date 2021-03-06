# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import uuid

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.fields import RichTextField
from mezzanine.core.models import RichText, TimeStamped
from mezzanine.pages.models import Page


class SurveyPage(Page, RichText):
    """
    Survey that contains a certain amount of questions.
    """
    instructions = RichTextField(_("Instructions"))
    cost = models.DecimalField(_("Cost"), max_digits=7, decimal_places=2)
    purchase_response = RichTextField(_("Purchase response"))
    completed_message = RichTextField(
        _("Completed message"),
        help_text=_("Message shown to users after completing the survey"))

    report_explanation = RichTextField(
        _("Explanation"),
        help_text=_("Helping content shown before the results' detail"))

    class Meta:
        verbose_name = _("survey page")
        verbose_name_plural = _("survey pages")


@python_2_unicode_compatible
class SurveyPurchaseCode(models.Model):
    """
    Code to gain access to a Survey
    """
    survey = models.ForeignKey(SurveyPage, related_name="purchase_codes")
    code = models.CharField(
        _("Code"), max_length=20, blank=True,
        help_text=_("If left blank it will be automatically generated"))
    uses_remaining = models.PositiveIntegerField(_("Remaining uses"), default=0)

    class Meta:
        verbose_name = _("purchase code")
        verbose_name_plural = _("purchase codes")
        unique_together = ("survey", "code")

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        """
        Generate a UUID if the code hasn't been defined
        """
        if not self.code:
            self.code = str(uuid.uuid4()).strip("-")[4:23]
        super(SurveyPurchaseCode, self).save(*args, **kwargs)


@python_2_unicode_compatible
class SurveyPurchase(TimeStamped):
    """
    A record of a user purchasing a Survey.
    """
    survey = models.ForeignKey(SurveyPage, related_name="purchases")
    purchaser = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="surveys")
    purchased_with_code = models.ForeignKey(SurveyPurchaseCode, blank=True, null=True)
    public_id = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)

    name = models.CharField(_("Name"), max_length=200)
    email = models.EmailField(_("Email"), max_length=300)
    transaction_id = models.CharField(_("Transaction ID"), max_length=200, blank=True)
    charge_details = models.TextField(_("Charge details"), blank=True)

    report_generated = models.DateTimeField(_("Report generated"), blank=True, null=True)

    class Meta:
        verbose_name = _("purchase")
        verbose_name_plural = _("purchases")

    def __str__(self):
        return "%s | %s" % (self.survey, self.name)
