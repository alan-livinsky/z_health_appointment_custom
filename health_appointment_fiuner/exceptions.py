# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.exceptions import UserError


class EndDateBeforeStartDate(UserError):
    pass


class NoRecordSelected(UserError):
    pass


class NoPatient(UserError):
    pass


class NoCompanyTimezone(UserError):
    pass


class PeriodTooLong(UserError):
    pass
