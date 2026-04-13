# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from datetime import timedelta, datetime, time
import pytz
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateAction, StateTransition, \
    Button
from trytond.pyson import PYSONEncoder
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction


class PrintDailyAppointmentStart(ModelView):
    'Print Daily Appointments Start'
    __name__ = 'gnuhealth.print.daily.appointment.start'

    appointment_date = fields.Date(u'Fecha de la cita', required=True)    
    health_profs = fields.Many2Many(
                    'gnuhealth.healthprofessional', None, None,
                    "Profesionales de salud", required=True)

    @staticmethod
    def default_health_profs():
        pool = Pool()
        HP = pool.get('gnuhealth.healthprofessional')
        hp = HP.search(
            [('id','>',0),
             ('active','=',True)])
        return [x.id for x in hp]


class PrintDailyAppointment(Wizard):
    'Print Daily Appointment'
    __name__ = 'gnuhealth.print.daily.appointment.wizard'

    start = StateView('gnuhealth.print.daily.appointment.start',
        'health_appointment_fiuner.print_daily_appointment_start_view_form', [
            Button('Cancelar', 'end', 'tryton-cancel'),
            Button('Imprimir Reporte - A4', 'print_a4', 'tryton-print'),
            Button('Imprimir Reporte - LEGAL', 'print_legal', 'tryton-print', default=True),
            ])

    print_a4 = StateAction(
        'health_appointment_fiuner.report_daily_appointment')

    print_legal = StateAction(
        'health_appointment_fiuner.report_daily_appointment_LEGAL')

    def fill_data(self):
        midnight = datetime.today().replace(hour=23,minute=59,second=59).time()
        return {
            'appointment_date': self.start.appointment_date,
            'health_profs': [x.id for x in self.start.health_profs],
            }

    def do_print_a4(self,action):
        print(2*'\n')
        print('impresion a4')
        print(2*'\n')
        return action, self.fill_data()

    def do_print_legal(self,action):
        print(2*'\n')
        print('impresion legal')
        print(2*'\n')
        return action, self.fill_data()
