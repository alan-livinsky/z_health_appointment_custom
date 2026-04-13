# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView
from trytond.wizard import Wizard, StateTransition, StateAction, StateView, Button
from trytond.transaction import Transaction
from trytond.pool import Pool
from trytond.pyson import PYSONEncoder
from trytond.i18n import gettext

from ..exceptions import NoRecordSelected, NoPatient



class OpenAppointmentPatient(Wizard):
    'Create Appointment Evaluation'
    __name__ = 'wizard.gnuhealth.appointment.patient'

    start_state = 'appointment_patient'
    appointment_patient = StateAction('health_appointment_fiuner.act_app_patient')

    def do_appointment_patient(self, action):
        appointment = Transaction().context.get('active_id')
        try:
            app_id = \
                Pool().get('gnuhealth.appointment').browse([appointment])[0]
        except:
            raise NoRecordSelected(gettext('msg_no_record_selected'))
        try:
            patient_id = app_id.patient.id
        except:
            raise NoPatient(gettext('msg_no_patient'))

        data = {'res_id': [patient_id]}
        action['views'].reverse()

        return action, data
