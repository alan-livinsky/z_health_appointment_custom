# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.report import Report
from trytond.pool import Pool

import string
from datetime import datetime, date, timedelta, time


class ReportAppointmentDaily(Report):
    __name__ = 'gnuhealth.report.daily'

    @classmethod
    def get_context(cls, records, data, name=None):
        pool = Pool()
        context = super(ReportAppointmentDaily, cls).get_context(records, data, name)
        appointments = None
        if 'appointment_date' in context['data']:
            print(2*'\n','daily report2', 2*'\n')
            Appointments = pool.get('gnuhealth.appointment')
            start_date = datetime.combine(context['data']['appointment_date'],time())
            end_date = datetime.combine(context['data']['appointment_date'],time(hour=23,minute=59))
            appointments = Appointments.search([
                ('appointment_date','>=',start_date),
                ('appointment_date','<=',end_date),
                ('healthprof','in',context['data']['health_profs']),
                ('patient','>',0),
                ],
                order=[('appointment_date', 'ASC')])
            context['appointment_date'] = context['data']['appointment_date']
            context['objects'] = appointments
        else:
            Date = pool.get('ir.date')
            appointments = records
            context['objects'] = appointments
            context['appointment_date'] = Date.today()

        institutions = set([str(x.institution.id) for x in appointments])
        context['institutions'] = institutions

        context['institution_hp'] = {}
        context['institution_institution'] = {}
        context['activities'] = set()
        context['health_profs'] = set()
        context['health_prof_name'] = {}
        context['health_prof_lastname'] = {}
        context['appointment_dates'] = set()
        for appt in appointments:
            if appt.healthprof:
                context['health_profs'].add(appt.healthprof.id)
                context['health_prof_name'][str(appt.healthprof.id)] =\
                    appt.healthprof.name.name
                context['health_prof_lastname'][str(appt.healthprof.id)] =\
                    appt.healthprof.name.lastname
                if not str(appt.institution.id) in context['institution_hp']:
                    context['institution_hp'][str(appt.institution.id)] = []
                context['institution_hp'][str(appt.institution.id)].append(appt.healthprof.id)
                if not str(appt.institution.id) in context['institution_institution']:
                    context['institution_institution'][str(appt.institution.id)] = appt.institution.name.name
                #context['institution_institution'][str(appt.institution.id)].append(appt.institution.name.name)
            if appt.appointment_date:
                context['appointment_dates'].add((appt.appointment_date\
                    +timedelta(hours=-3)).date())
        context['page_break'] = '\n'#TODO change \n for the correspondient character to put a page break on the odt
        return context
