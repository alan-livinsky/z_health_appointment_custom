# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from trytond.report import Report
from trytond.pool import Pool
from trytond.transaction import Transaction


__all__ = ['AppointmentReport']

#TODO merge this function and the next one
def get_population_by_speciality(appointments,year_1,year_2,speciality,gender):
    if year_2 == 0:
        return len([x for x in appointments\
            if x.patient.gender == gender\
                and x.patient.name.dob > year_1\
                and x.speciality == speciality
                    ])
    elif year_1 == 0:
        return len([x for x in appointments\
            if x.patient.gender == gender\
                and x.patient.name.dob < year_2\
                and x.speciality == speciality
                    ])
    else:
        return len([x for x in appointments\
            if x.patient.gender == gender\
                and x.patient.name.dob >= year_1\
                and x.patient.name.dob < year_2\
                and x.speciality == speciality
                    ])

def get_population_by_hp(appointments,year_1,year_2,healthprof,gender):
    if year_2 ==0:
        return len([x for x in appointments\
            if x.patient.gender == gender\
                and x.patient.name.dob > year_1\
                and x.healthprof == healthprof
                    ])
    elif year_1 ==0:
        return len([x for x in appointments\
            if x.patient.gender == gender\
                and x.patient.name.dob < year_2\
                and x.healthprof == healthprof
                    ])
    else:
        return len([x for x in appointments\
            if x.patient.gender == gender\
                and x.patient.name.dob >= year_1\
                and x.patient.name.dob < year_2\
                and x.healthprof == healthprof
                    ])


class AppointmentReport(Report):
    __name__ = 'gnuhealth.appointment.report'

    @classmethod
    def get_context(cls, records, data, name=None):
        context = super().get_context(records, data, name)
        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        start_date = context['data']['start_date']
        context['start_date'] = context['data']['start_date']

        end_date = context['data']['end_date']
        context['end_date'] = context['data']['end_date']

        confirmed = 'confirmed' if context['data']['confirmed'] else ''
        context['confirmed'] = 'confirmed' if context['data']['confirmed'] else ''

        checked_in = 'checked_in' if context['data']['check_in'] else ''
        context['check_in'] = 'checked_in' if context['data']['check_in'] else ''

        done = 'done' if context['data']['done'] else ''
        context['done'] = 'checked_in' if context['data']['done'] else ''

        appointments = Appointment.search([
            ('appointment_date','>=',start_date),
            ('appointment_date','<',end_date),
            ('state','in',[checked_in, confirmed, done]),
            ('patient.name.dob','!=',None),
            ])

        specialities = set()
        context['specialities_doctor'] = set()
        context['specialities_non_doctor'] = set()
        healthprofs = set()
        context['healthprofs_doctor'] = set()
        context['healthprofs_non_doctor'] = set()
        for appointment in appointments:
            if appointment.speciality and appointment.healthprof\
            and appointment.healthprof.is_doctor:
                context['specialities_doctor'].add(appointment.speciality) 
                specialities.add(appointment.speciality)
            elif appointment.speciality:
                context['specialities_non_doctor'].add(appointment.speciality)
                specialities.add(appointment.speciality)

            if appointment.healthprof and appointment.healthprof.is_doctor:
                context['healthprofs_doctor'].add(appointment.healthprof) 
                healthprofs.add(appointment.healthprof)
            elif appointment.healthprof:
                context['healthprofs_non_doctor'].add(appointment.healthprof)
                healthprofs.add(appointment.healthprof)

        year_ago_1 = (end_date + relativedelta(year=date.today().year-1)).date()
        year_ago_2 = (end_date + relativedelta(year=date.today().year-2)).date()
        year_ago_5 = (end_date + relativedelta(year=date.today().year-5)).date()
        year_ago_10 = (end_date + relativedelta(year=date.today().year-10)).date()
        year_ago_15 = (end_date + relativedelta(year=date.today().year-15)).date()
        year_ago_49 = (end_date + relativedelta(year=date.today().year-50)).date()

        context['spec_doctor_total_under_1'] = 0
        context['spec_doctor_total_1'] = 0
        context['spec_doctor_total_2_4'] = 0
        context['spec_doctor_total_5_9'] = 0
        context['spec_doctor_total_10_14'] = 0
        context['spec_doctor_total_15_49'] = 0
        context['spec_doctor_total_50_beyond'] = 0
        context['spec_doctor_total'] = 0
        context['spec_doctor_total_assured'] = 0
        context['spec_doctor_total_unassured'] = 0

        context['spec_non_doctor_total_under_1'] = 0
        context['spec_non_doctor_total_1'] = 0
        context['spec_non_doctor_total_2_4'] = 0
        context['spec_non_doctor_total_5_9'] = 0
        context['spec_non_doctor_total_10_14'] = 0
        context['spec_non_doctor_total_15_49'] = 0
        context['spec_non_doctor_total_50_beyond'] = 0
        context['spec_non_doctor_total'] = 0
        context['spec_non_doctor_total_assured'] = 0
        context['spec_non_doctor_total_unassured'] = 0

        total_under_1 = total_1 =  total_2_4 = total_5_9 = total_10_14 =  0
        total_15_49 = total_50_beyond = total = 0
        total_assured = total_unassured = 0

        context['speciality_row'] = {}

        for speciality in specialities:
            context['speciality_row'][str(speciality)] = {}
            f_under_1 = get_population_by_speciality(
                appointments, year_ago_1, 0,
                speciality, 'f')
            m_under_1 = get_population_by_speciality(
                appointments, year_ago_1, 0,
                speciality, 'm')
            context['speciality_row'][str(speciality)]['f_under_1'] = f_under_1
            context['speciality_row'][str(speciality)]['m_under_1'] = m_under_1
            total_under_1 = f_under_1 + m_under_1

            f_1 = get_population_by_speciality(
                appointments, year_ago_2, year_ago_1,
                speciality, 'f')
            m_1 = get_population_by_speciality(
                appointments, year_ago_2, year_ago_1,
                speciality, 'm')
            context['speciality_row'][str(speciality)]['f_1'] = f_1
            context['speciality_row'][str(speciality)]['m_1'] = m_1
            total_1 = f_1 + m_1

            f_2_4 = get_population_by_speciality(
                appointments, year_ago_5, year_ago_2,
                speciality, 'f')
            m_2_4 = get_population_by_speciality(
                appointments, year_ago_5, year_ago_2,
                speciality, 'm')
            context['speciality_row'][str(speciality)]['f_2_4'] = f_2_4
            context['speciality_row'][str(speciality)]['m_2_4'] = m_2_4
            total_2_4 = f_2_4 + m_2_4

            f_5_9 = get_population_by_speciality(
                appointments, year_ago_10, year_ago_5,
                speciality, 'f')
            m_5_9 = get_population_by_speciality(
                appointments, year_ago_10, year_ago_5,
                speciality, 'm')
            context['speciality_row'][str(speciality)]['f_5_9'] = f_5_9
            context['speciality_row'][str(speciality)]['m_5_9'] = m_5_9
            total_5_9 = f_5_9 + m_5_9

            f_10_14 = get_population_by_speciality(
                appointments, year_ago_15, year_ago_10,
                speciality, 'f')
            m_10_14 = get_population_by_speciality(
                appointments, year_ago_15, year_ago_10,
                speciality, 'm')
            context['speciality_row'][str(speciality)]['f_10_14'] = f_10_14
            context['speciality_row'][str(speciality)]['m_10_14'] = m_10_14
            total_10_14 = f_10_14 + m_10_14

            f_15_49 = get_population_by_speciality(
                appointments, year_ago_49, year_ago_15,
                speciality, 'f')
            m_15_49 = get_population_by_speciality(
                appointments, year_ago_49, year_ago_15,
                speciality, 'm')
            context['speciality_row'][str(speciality)]['f_15_49'] = f_15_49
            context['speciality_row'][str(speciality)]['m_15_49'] = m_15_49
            total_15_49 = f_15_49 + m_15_49

            f_50_beyond = get_population_by_speciality(
                appointments, 0, year_ago_49,
                speciality, 'f')
            m_50_beyond = get_population_by_speciality(
                appointments, 0, year_ago_49,
                speciality, 'm')
            context['speciality_row'][str(speciality)]['f_50_beyond'] = f_50_beyond
            context['speciality_row'][str(speciality)]['m_50_beyond'] = m_50_beyond
            total_50_beyond = f_50_beyond + m_50_beyond

            context['speciality_row'][str(speciality)]['total'] =\
                len([x for x in appointments\
                    if x.speciality == speciality
                    ])

            total = f_under_1 + f_2_4 + f_5_9 + f_10_14 + f_15_49 + f_50_beyond\
                + m_under_1 + m_2_4 + m_5_9 + m_10_14 + m_15_49 + m_50_beyond

            assured = len([x for x in appointments\
                if x.patient.current_insurance != None\
                and x.speciality == speciality
                ])
            context['speciality_row'][str(speciality)]['assured'] = assured

            unassured = len([x for x in appointments\
                if x.patient.current_insurance == None\
                and x.speciality == speciality
                ])
            context['speciality_row'][str(speciality)]['unassured'] = unassured

            if speciality in context['specialities_doctor']:
                context['spec_doctor_total_under_1'] += total_under_1
                context['spec_doctor_total_1'] += total_1
                context['spec_doctor_total_2_4'] += total_2_4
                context['spec_doctor_total_5_9'] += total_5_9
                context['spec_doctor_total_10_14'] += total_10_14
                context['spec_doctor_total_15_49'] += total_15_49
                context['spec_doctor_total_50_beyond'] += total_50_beyond
                context['spec_doctor_total'] += total
                context['spec_doctor_total_assured'] += assured
                context['spec_doctor_total_unassured'] += unassured
            else:
                context['spec_non_doctor_total_under_1'] += total_under_1
                context['spec_doctor_total_1'] += total_1
                context['spec_non_doctor_total_2_4'] += total_2_4
                context['spec_non_doctor_total_5_9'] += total_5_9
                context['spec_non_doctor_total_10_14'] += total_10_14
                context['spec_non_doctor_total_15_49'] += total_15_49
                context['spec_non_doctor_total_50_beyond'] += total_50_beyond
                context['spec_non_doctor_total'] += total
                context['spec_non_doctor_total_assured'] += assured
                context['spec_non_doctor_total_unassured'] += unassured

        context['hp_doctor_total_under_1'] = 0
        context['hp_doctor_total_1'] = 0
        context['hp_doctor_total_2_4'] = 0
        context['hp_doctor_total_5_9'] = 0
        context['hp_doctor_total_10_14'] = 0
        context['hp_doctor_total_15_49'] = 0
        context['hp_doctor_total_50_beyond'] = 0
        context['hp_doctor_total'] = 0
        context['hp_doctor_total_assured'] = 0
        context['hp_doctor_total_unassured'] = 0

        context['hp_non_doctor_total_under_1'] = 0
        context['hp_non_doctor_total_1'] = 0
        context['hp_non_doctor_total_2_4'] = 0
        context['hp_non_doctor_total_5_9'] = 0
        context['hp_non_doctor_total_10_14'] = 0
        context['hp_non_doctor_total_15_49'] = 0
        context['hp_non_doctor_total_50_beyond'] = 0
        context['hp_non_doctor_total'] = 0
        context['hp_non_doctor_total_assured'] = 0
        context['hp_non_doctor_total_unassured'] = 0

        total_under_1 = total_1 =  total_2_4 = total_5_9 = total_10_14 =  0
        total_15_49 = total_50_beyond = total = 0
        total_assured = total_unassured = 0

        context['healthprof_row'] = {}

        for healthprof in healthprofs:
            context['healthprof_row'][str(healthprof)] = {}
            f_under_1 = get_population_by_hp(
                appointments,year_ago_1,0,healthprof,'f')
            m_under_1 = get_population_by_hp(
                appointments,year_ago_1,0,healthprof,'m')
            context['healthprof_row'][str(healthprof)]['f_under_1'] = f_under_1
            context['healthprof_row'][str(healthprof)]['m_under_1'] = m_under_1
            total_under_1 = f_under_1 + m_under_1

            f_1 = get_population_by_hp(
                appointments,year_ago_2,year_ago_1,healthprof,'f')
            m_1 = get_population_by_hp(
                appointments,year_ago_2,year_ago_1,healthprof,'m')
            context['healthprof_row'][str(healthprof)]['f_1'] = f_1
            context['healthprof_row'][str(healthprof)]['m_1'] = m_1
            total_1 = f_1 + m_1
 
            f_2_4 = get_population_by_hp(
                appointments,year_ago_5,year_ago_2,healthprof,'f')
            m_2_4 = get_population_by_hp(
                appointments,year_ago_5,year_ago_2,healthprof,'m')
            context['healthprof_row'][str(healthprof)]['f_2_4'] = f_2_4
            context['healthprof_row'][str(healthprof)]['m_2_4'] = m_2_4
            total_2_4 = f_2_4 + m_2_4

            f_5_9 = get_population_by_hp(
                appointments,year_ago_10,year_ago_5,healthprof,'f')
            m_5_9 = get_population_by_hp(
                appointments,year_ago_10,year_ago_5,healthprof,'m')
            context['healthprof_row'][str(healthprof)]['f_5_9'] = f_5_9
            context['healthprof_row'][str(healthprof)]['m_5_9'] = m_5_9
            total_5_9 = f_5_9 + m_5_9

            f_10_14 = get_population_by_hp(
                appointments,year_ago_15,year_ago_10,healthprof,'f')
            m_10_14 = get_population_by_hp(
                appointments,year_ago_15,year_ago_10,healthprof,'m')
            context['healthprof_row'][str(healthprof)]['f_10_14'] = f_10_14
            context['healthprof_row'][str(healthprof)]['m_10_14'] = m_10_14
            total_10_14 = f_10_14 + m_10_14

            f_15_49 = get_population_by_hp(
                appointments,year_ago_49,year_ago_15,healthprof,'f')
            m_15_49 = get_population_by_hp(
                appointments,year_ago_49,year_ago_15,healthprof,'m')
            context['healthprof_row'][str(healthprof)]['f_15_49'] = f_15_49
            context['healthprof_row'][str(healthprof)]['m_15_49'] = m_15_49
            total_15_49 = f_15_49 + m_15_49

            f_50_beyond = get_population_by_hp(
                appointments,0,year_ago_49,healthprof,'f')
            m_50_beyond = get_population_by_hp(
                appointments,0,year_ago_49,healthprof,'m')
            context['healthprof_row'][str(healthprof)]['f_50_beyond'] = f_50_beyond
            context['healthprof_row'][str(healthprof)]['m_50_beyond'] = m_50_beyond
            total_50_beyond = f_50_beyond + m_50_beyond

            context['healthprof_row'][str(healthprof)]['total'] =\
                len([x for x in appointments\
                    if x.healthprof == healthprof
                    ])

            assured = len([x for x in appointments\
                if x.patient.current_insurance != None\
                and x.healthprof == healthprof
                ])
            context['healthprof_row'][str(healthprof)]['assured'] = assured

            unassured = len([x for x in appointments\
                if x.patient.current_insurance == None\
                and x.healthprof == healthprof
                ])
            context['healthprof_row'][str(healthprof)]['unassured'] = unassured

            total = f_under_1 + f_2_4 + f_5_9 + f_10_14\
                + f_15_49 + f_50_beyond + m_under_1 + m_2_4 + m_5_9\
                + m_10_14 + m_15_49 + m_50_beyond
            if healthprof.is_doctor:
                context['hp_doctor_total_under_1'] += total_under_1
                context['hp_doctor_total_1'] += total_1
                context['hp_doctor_total_2_4'] += total_2_4
                context['hp_doctor_total_5_9'] += total_5_9
                context['hp_doctor_total_10_14'] += total_10_14
                context['hp_doctor_total_15_49'] += total_15_49
                context['hp_doctor_total_50_beyond'] += total_50_beyond
                context['hp_doctor_total'] += total
                context['hp_doctor_total_assured'] += assured
                context['hp_doctor_total_unassured'] += unassured
            else:
                context['hp_non_doctor_total_under_1'] += total_under_1
                context['hp_non_doctor_total_1'] += total_1
                context['hp_non_doctor_total_2_4'] += total_2_4
                context['hp_non_doctor_total_5_9'] += total_5_9
                context['hp_non_doctor_total_10_14'] += total_10_14
                context['hp_non_doctor_total_15_49'] += total_15_49
                context['hp_non_doctor_total_50_beyond'] += total_50_beyond
                context['hp_non_doctor_total'] += total
                context['hp_non_doctor_total_assured'] += assured
                context['hp_non_doctor_total_unassured'] += unassured
        return context
