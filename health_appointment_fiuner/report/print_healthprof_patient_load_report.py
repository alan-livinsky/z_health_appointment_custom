from trytond.report import Report
from trytond.pool import Pool

from datetime import datetime, time


class PrintHealthProfPatientLoadReport(Report):
    __name__ = 'gnuhealth.appointment.print_hp_patient_load.report'

    @classmethod
    def get_context(cls, records, header, data):
        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        HP = pool.get('gnuhealth.healthprofessional')
        context = super().get_context(records, header, data)

        hps = HP.search([
            ('id', 'in', data['hps'])
            ])
        context['hps'] = {}
        context['load'] = {}
        for hp in hps:
            context['hps'][str(hp.id)] = {
                'name': hp.rec_name
                }
            context['load'][str(hp.id)] = []
        start_date = datetime.combine(context['data']['start_date'],time())
        end_date = datetime.combine(context['data']['end_date'],
                    time(hour=23,minute=59))

        for hp in hps:
            appointments = Appointment.search([
                ('healthprof', '=', hp.id),
                ('appointment_date', '>=', start_date),
                ('appointment_date', '<=', end_date)
                ])
            patients = list(set([app.patient for app in appointments if app.patient]))
            for patient in patients:
                context['load'][str(hp.id)].append(patient)
        return context
