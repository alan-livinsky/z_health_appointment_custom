# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from datetime import timedelta, datetime, time
import pytz

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.i18n import gettext

from ..exceptions import (NoCompanyTimezone, EndDateBeforeStartDate,
        PeriodTooLong)


class CreateAppointmentStart(metaclass=PoolMeta):
    'Create Appointments Start'
    __name__ = 'gnuhealth.calendar.create.appointment.start'

    daily_appointment_quantity = fields.Integer(u'Cantidad de turnos por día',
        help="Cantidad de turnos a otorgar")
    visit_type = fields.Selection([
        (None, ''),
        ('new', 'New health condition'),
        ('followup', 'Followup'),
        ('well_child', 'Well Child visit'),
        ('well_woman', 'Well Woman visit'),
        ('well_man', 'Well Man visit'),
        ], 'Visit', sort=False, required=True)

    @fields.depends('appointment_minutes',
        'time_end', 'time_start', 'daily_appointment_quantity')
    def on_change_with_daily_appointment_quantity(self):
        # Return the quantity of appointment per day
        if self.appointment_minutes and self.time_end and self.time_start and not self.daily_appointment_quantity:
            delta_hours = self.time_end.hour - self.time_start.hour
            delta_minutes = self.time_end.minute - self.time_start.minute
            delta_time = (delta_hours*60+delta_minutes) if delta_hours>0 else 0
            appointment_quantity = int((delta_time)/self.appointment_minutes)
            return appointment_quantity
        return self.daily_appointment_quantity

    @fields.depends('daily_appointment_quantity',
         'time_end', 'time_start', 'appointment_minutes')
    def on_change_with_appointment_minutes(self):
        # Return the quantity of appointment per day
        if self.daily_appointment_quantity and self.time_end and self.time_start and not self.appointment_minutes:
            delta_hours = self.time_end.hour - self.time_start.hour
            delta_minutes = self.time_end.minute - self.time_start.minute
            delta_time = (delta_hours*60+delta_minutes) if delta_hours>0 else 0
            appointment_minutes = int((delta_time)/self.daily_appointment_quantity)
            return appointment_minutes
        return self.appointment_minutes

    @fields.depends('healthprof')
    def on_change_date_start(self):
        if self.healthprof:
            self.monday = self.healthprof.monday
            self.tuesday = self.healthprof.tuesday
            self.wednesday = self.healthprof.wednesday
            self.thursday = self.healthprof.thursday
            self.friday = self.healthprof.friday
            self.saturday = self.healthprof.saturday
            self.sunday= self.healthprof.sunday
            self.time_start = self.healthprof.time_start
            self.time_end = self.healthprof.time_end
            self.appointment_minutes = self.healthprof.appointment_minutes
            self.daily_appointment_quantity = self.healthprof.daily_appointment_quantity

    @staticmethod
    def default_visit_type():
        return 'new'


class CreateAppointment(metaclass=PoolMeta):
    'Create Appointment'
    __name__ = 'gnuhealth.calendar.create.appointment'

    def transition_create_(self):
        '''Overwrite transition_create_ function '''
        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        Company = pool.get('company.company')

        timezone = None
        company_id = Transaction().context.get('company')
        if company_id:
            company = Company(company_id)
            if company.timezone:
                timezone = pytz.timezone(company.timezone)
            else:
                raise NoCompanyTimezone(gettext('msg_no_company_timezone'))

        visit_type = self.start.visit_type
        appointments = []

        # Iterate over days
        day_count = (self.start.date_end - self.start.date_start).days + 1

        # Validate dates
        if (self.start.date_start and self.start.date_end):
            if (self.start.date_end < self.start.date_start):
                raise EndDateBeforeStartDate(gettext('msg_end_date_before_start_date'))

            if (day_count > 32):
                raise PeriodTooLong(gettext('msgperiod_too_long'))

        for single_date in (self.start.date_start + timedelta(n)
            for n in range(day_count)):
            if ((single_date.weekday() == 0 and self.start.monday)
            or (single_date.weekday() == 1 and self.start.tuesday)
            or (single_date.weekday() == 2 and self.start.wednesday)
            or (single_date.weekday() == 3 and self.start.thursday)
            or (single_date.weekday() == 4 and self.start.friday)
            or (single_date.weekday() == 5 and self.start.saturday)
            or (single_date.weekday() == 6 and self.start.sunday)):
                # Iterate over time
                dt = datetime.combine(
                    single_date, self.start.time_start)
                dt = timezone.localize(dt)
                dt = dt.astimezone(pytz.utc) 
                dt_end = datetime.combine(
                    single_date, self.start.time_end)
                dt_end = timezone.localize(dt_end)
                dt_end = dt_end.astimezone(pytz.utc) 
                while dt < dt_end:
                    appointment = {
                        'healthprof': self.start.healthprof.id,
                        'speciality': self.start.specialty.id,
                        'institution': self.start.institution.id,
                        'appointment_date': dt,
                        'appointment_date_end': dt +
                            timedelta(minutes=self.start.appointment_minutes),
                        'state': 'free',
                        'visit_type': visit_type,
                        }
                    appointments.append(appointment)
                    dt += timedelta(minutes=self.start.appointment_minutes)
        if appointments:
            Appointment.create(appointments)
        return 'open_'
        return res    
    
    
