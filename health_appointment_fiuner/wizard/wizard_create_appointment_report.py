# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from datetime import datetime, timedelta
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button,\
    StateAction
from trytond.transaction import Transaction
from trytond.pool import Pool
import calendar


class AppointmentReportStart(ModelView):
    'Request Prescription Batch Start'
    __name__ = 'gnuhealth.appointment.report.start'
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    confirmed = fields.Boolean('Confirmed')
    check_in = fields.Boolean('Checked in', help='Check in')
    done = fields.Boolean('Done')

    @staticmethod
    def default_confirmed():
        return True

    @staticmethod
    def default_check_in():
        return True

    @staticmethod
    def default_done():
        return True

    @staticmethod
    def default_start_date():
        first_day = (datetime.now().replace(day=1)).date()
        return first_day

    @staticmethod
    def default_end_date():
        month_range = calendar.monthrange(datetime.now().year,datetime.now().month)[1]
        last_day = (datetime.now().replace(day=month_range)).date()
        return last_day


class AppointmentReportWizard(Wizard):
    'Request Prescription Batch'
    __name__ = 'gnuhealth.appointment.report.wizard'

    start = StateView('gnuhealth.appointment.report.start',
        'health_appointment_fiuner.statistical_report_appointment_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),            
            Button('Print Report', 'request', 'tryton-print', default=True),
            ])
    request = StateAction(
        'health_appointment_fiuner.report_appointment_report')

    def fill_data(self):
        midnight = datetime.today().replace(hour=23,minute=59,second=59).time()
        return {
            'start_date': datetime.combine(self.start.start_date, datetime.min.time()),
            'end_date': datetime.combine(self.start.end_date, midnight),
            'confirmed': self.start.confirmed,
            'check_in': self.start.check_in,
            'done': self.start.done,
            }

    def do_request(self,action):
        return action, self.fill_data()
