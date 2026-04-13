# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.wizard import Wizard, StateView, Button, StateTransition, StateAction
from trytond.model import ModelView, fields
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import Eval, Not, Bool, Equal
from trytond.i18n import gettext

from ..exceptions import EndDateBeforeStartDate

import csv
import sys
from io import StringIO
from datetime import datetime, date, time, timedelta


class CreateDiaryAppointmentReportStart(ModelView):
    'Appointment Report Start'
    __name__ = 'gnuhealth.appointment.diary_report.start'

    report_ = fields.Selection([
        ('create_appointment_report', 'Appointment Report'),
         ],'Appointment Report',required=True,sort=False)
    start_date = fields.DateTime('Start Date', required=True)
    end_date = fields.DateTime('End Date', required=True)
    professional = fields.Many2One('gnuhealth.healthprofessional',
        'Health Prof', help="Health professional", required=True)

    @staticmethod
    def default_report_():
        return 'create_appointment_report'

    @staticmethod
    def default_start_date():
        d = date.today()
        t = time(3, 0)
        return datetime.combine(d, t)

    @staticmethod
    def default_end_date():
        d = date.today() + timedelta(days=1) 
        t = time(3, 0, 0)
        return datetime.combine(d, t)


class CreateDiaryAppointmentReportWizard(Wizard):
    'Appointment Report Wizard'
    __name__ = 'gnuhealth.appointment.diary_report.wizard'

    start = StateView('gnuhealth.appointment.diary_report.start',
        'health_appointment_fiuner.create_appointment_report_start_view',[
                Button('Cancel','end','tryton-cancel'),
                Button('Print Report','prevalidate','tryton-ok',default=True),
                ])
    prevalidate = StateTransition()
    create_appointment_report =\
        StateAction('health_appointment_fiuner.act_gnuhealth_appointment_report')

    def transition_prevalidate(self):
        if self.start.end_date < self.start.start_date:
            raise EndDateBeforeStartDate(gettext('msg_end_date_before_start_date'))
        return self.start.report_

    def fill_data(self):
        start = self.start.start_date
        end = self.start.end_date
        healthprof = self.start.professional.id
        return {
            'start':start,
            'healthprof':healthprof,
            'end':end
            }

    def do_create_appointment_report(self, action):
        data = self.fill_data()
        return action, data
