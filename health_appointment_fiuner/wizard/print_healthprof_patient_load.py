from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.pool import Pool

from datetime import date, datetime, time


class PrintHealthProfPatientLoadStart(ModelView):
    "Print Health Prof Patient Load - Start"
    __name__ = 'gnuhealth.appointment.print_hp_patient_load.start'

    start_date = fields.Date('Start date', required=True)
    end_date = fields.Date('End date', required=True)
    add_hps_period = fields.Boolean('Add health professional in this period')
    hps = fields.Many2Many('gnuhealth.healthprofessional', None, None,
            "Health Professional", required=True)

    @staticmethod
    def default_start_date():
        return date.today()

    @staticmethod
    def default_add_hps_period():
        return False

    @fields.depends('start_date', 'end_date', 'add_hps_period')
    def on_change_with_hps(self, name=None):
        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        if self.start_date and self.end_date and self.add_hps_period:
            start_date = datetime.combine(self.start_date,
                        time(0, 0))
            end_date = datetime.combine(self.end_date,
                        time(23, 59))
            appointments = Appointment.search([
                ('appointment_date', '>', start_date),
                ('appointment_date', '<', end_date)
                ])
            hps = list(set([app.healthprof.id for app in appointments
                            if app.healthprof]))
            return hps
        return []


class PrintHealthProfPatientLoadWizard(Wizard):
    "Print Health Prof Patient Load - Wizard"
    __name__ = 'gnuhealth.appointment.print_hp_patient_load.wizard'

    start = StateView('gnuhealth.appointment.print_hp_patient_load.start',
        'health_appointment_fiuner.print_hp_patient_load_start',[
                Button('Cancel','end','tryton-cancel'),
                Button('Print','print_','tryton-ok',default=True),
                ])

    print_ = StateAction('health_appointment_fiuner.act_print_hp_patient_load_report')

    def do_print_(self, actions):
        data = {
            'start_date': self.start.start_date,
            'end_date': self.start.end_date,
            'hps': [hp.id for hp in self.start.hps]
            }
        return actions, data
