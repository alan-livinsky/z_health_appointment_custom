# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from trytond.report import Report

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from trytond.transaction import Transaction


class AppointmentDiaryReport(Report):
    'Appointment Report'
    __name__ = 'gnuhealth.appointment.appointment_report'

    @classmethod
    def get_context(cls, records, data, name=None):
        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        Healthprofessional =pool.get('gnuhealth.healthprofessional')
        User = Pool().get('res.user')
        user = User(Transaction().user)
        context = super(AppointmentDiaryReport, cls).get_context(records, data, name) #es un diccionario

        if context['data']:
            start = context['data']['start']
            end = context['data']['end']
            final = context['data']['end'] + timedelta(days=1)
            healthprof = context['data']['healthprof']

            appointment = Appointment.search([
                ('appointment_date','>=',start),
                ('appointment_date','<',final),
                ('healthprof.id','=',healthprof),
                ('healthprof.institution.name.id','=',user.company.party.id),
                ('patient', '!=', None)
                ])

            healthprofessional = Healthprofessional.search([('id','=',healthprof)])

            context['healthprof'] = healthprofessional[0].name.rec_name
            context['specialty'] = \
                healthprofessional[0].main_specialty and healthprofessional[0].main_specialty.specialty.name or\
                healthprofessional[0].specialties and healthprofessional[0].specialties[0].specialty.name
            context['current_date'] = date.today()

            if healthprofessional[0].main_specialty and healthprofessional[0].main_specialty.specialty.name == 'Odontología':
                context['odontology'] = True
            else:
               context['odontology'] = False

            context['lines'] = []
            for x in appointment:
                aux = []
                if context['odontology'] == True:
                    aux.append(x.patient.puid)
                    aux.append(x.patient.name.rec_name)
                    context['lines'].append(aux)
                else:
                    aux.append(x.patient.puid)
                    aux.append(x.patient.name.rec_name)
                    aux.append(x.patient.age_float)
                    aux.append(x.patient.gender)
                    adress = ''
                    if x.patient.name.addresses[0].street is not None:
                        adress = x.patient.name.addresses[0].street
                    if x.patient.name.addresses[0].city is not None:
                        adress+= ", " + x.patient.name.addresses[0].city
                    if x.patient.name.addresses[0].subdivision is not None:
                        adress+= ", " + x.patient.name.addresses[0].subdivision.name
                    aux.append(adress)
                    current_insurance = ''
                    if x.patient.current_insurance is not None:
                        current_insurance = x.patient.current_insurance.company.name
                    aux.append(current_insurance)
                    context['lines'].append(aux)
        return context
