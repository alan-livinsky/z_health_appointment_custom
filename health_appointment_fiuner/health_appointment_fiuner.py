# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import Or, Eval, Not, Bool, Equal
from trytond.exceptions import UserError
from trytond.i18n import gettext

from ..health.core import compute_age_from_dates

from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta

import calendar
import re


class Appointment(metaclass = PoolMeta):
    'Appointment Data'
    __name__ = 'gnuhealth.appointment'

    qr_code = fields.Char('QR Code')
    age = fields.Function(
        fields.Float('Age', help="Edad al momento de la cita"),
        'on_change_with_age', searcher='search_age')
    dni = fields.Function(
        fields.Char('DNI', readonly=True),
        'on_change_with_dni')
    hc = fields.Function(
        fields.Char('HC', readonly=True),
        'on_change_with_hc')
    phone = fields.Function(
        fields.Char('Phone'),
        'get_party_phone', setter='set_party_phone')
    current_insurance = fields.Function(
        fields.Many2One('gnuhealth.insurance', 'Insurance',readonly=True),
        'on_change_with_current_insurance')
    appointment_kind = fields.Selection([
        (None,''),
        ('sponteneous_appointment','Spontaneous'),
        ('active_uptake','Active uptake'),
        ('scheduled_appointment','Scheduled appointment'),
        ('protected_appointment','Protected appointment'),
        ], 'Appointment kind',sort=False)
    gender = fields.Function(
        fields.Selection([
            (None, ''),
            ('m', 'Masculino'),
            ('f', 'Femenino')
            ],'Sex'),
        'on_change_with_gender')
    chronic = fields.Function(
        fields.Selection([
            (None, ''),
            ('Si', 'Si'),
            ('No', 'No')
            ],'Cronico'),
        'on_change_with_chronic')
    absentism_warning = fields.Function(
        fields.Boolean("Absentism warning",
            help="Warn if three times consecutives the "
            "patient didn't show or cancelled the appointment"),
        'on_change_with_absentism_warning')

    @fields.depends('patient', 'appointment_date')
    def on_change_with_age(self, name=None):
        if self.patient and self.appointment_date and self.patient.dob:
            age = compute_age_from_dates(self.patient.dob, None, None, None,
                        'raw_age', self.appointment_date.date())
            if (age[0] + age[1] + age[2]) > 0:
                return round(age[0] + age[1]/12 + age[2]/365, 2)
        return None

    @fields.depends('patient')
    def on_change_with_dni(self, name=None):
        if self.patient:
            return self.patient.puid
        return None

    @fields.depends('patient')
    def on_change_with_hc(self, name=None):
        if self.patient:
            return self.patient.hc
        return None

    @fields.depends('patient')
    def on_change_with_current_insurance(self, name=None):
        if self.patient and self.patient.current_insurance:
            return self.patient.current_insurance.id
        return None

    @fields.depends('patient')
    def on_change_with_gender(self, name=None):
        if self.patient:
            return self.patient.gender
        return None

    @fields.depends('patient')
    def on_change_with_chronic(self, name=None):
        if self.patient:
            return self.patient.cronico
        return None

    @fields.depends('qr_code')
    def on_change_qr_code(self):
        '''
        Example ID to be parsed:
        00305133441"MIAPELLIDO"MI NOMBRE"M"20123456"A"20-12-1950"02-10-2014"207
        '''
        Patient = Pool().get('gnuhealth.patient')
        code = self.qr_code
        self.comments = code
        if len(code) > 60:
            elements = re.sub('[^0-9a-zA-Z ]+', '*', code)
            elements = elements.split('*')
            idup = elements[4]
            res = Patient.search([('puid', '=', idup)])
            if res:
                self.qr_code = None
                self.patient = res[0].id
                self.dni = res[0].puid
                self.gender = res[0].gender
                self.age = res[0].age
                self.current_insurance = res[0].current_insurance.id if self.patient.current_insurance else None
                self.gender = res[0].name.gender
                self.chronic = res[0].cronico
                self.phone = res[0].name.phone
                self.state = 'confirmed'
                self.visit_type = 'new'
            else:
                self.qr_code = None
                self.patient = None
                self.dni = None
                self.gender = None
                self.age = None
                self.current_insurance = None
                self.gender = None
                self.chronic = None
                self.phone = None
                self.state = 'free'
                self.visit_type = None
                raise UserError(gettext('health_appointment_fiuner.msg_not_dni'))

    @fields.depends('patient', 'appointment_date')
    def on_change_with_absentism_warning(self, name=None):
        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        if self.patient and self.appointment_date:
            appointments = Appointment.search([
                ('patient', '=', self.patient.id),
                ('appointment_date', '<', self.appointment_date)],
                order=[('appointment_date', 'DESC')]
                )
            print(appointments)
            if len(appointments) > 2:
                criteria = all([app.state in ['no_show', 'user_cancelled']
                                    for app in appointments[:3]])
                print([app.state for app in appointments[:3]])
                print(criteria)
                return criteria
        return False

    @classmethod
    def validate(cls, appointments):
        super(Appointment, cls).validate(appointments)
        for appointment in appointments:
            appointment.check_health_professional()

    def check_health_professional(self):
        if not self.healthprof and self.state != 'free':
            raise UserError('Debe asignar un Profesional al Turno')

    @fields.depends('patient')
    def on_change_patient(self):
        if self.patient:
                self.dni = self.patient.puid
                self.gender = self.patient.gender
                self.age = self.patient.age
                self.current_insurance = self.patient.current_insurance.id if self.patient.current_insurance else None
                self.gender = self.patient.name.gender
                self.chronic = self.patient.cronico
                self.phone = self.patient.name.phone
                self.state = 'confirmed'
                self.visit_type = 'new'
        else:
                self.dni = None
                self.gender = None
                self.age = None
                self.current_insurance = None
                self.gender = None
                self.chronic = None
                self.phone = None
                self.state = 'free'
                self.visit_type = None

    @classmethod
    def get_party_phone(cls, appointment, name=None):
        result = {}
        for a in appointment:
            result[a.id] = a.patient and a.patient.name.phone or ''
        return result

    @classmethod
    def set_party_phone(cls, appointment, name, value):
        pool = Pool()
        ContactMechanism = pool.get('party.contact_mechanism')
        for a in appointment:
            if not a.patient:
                continue
            party_phone = ContactMechanism.search([
                ('party', '=', a.patient.name),
                ('type', '=', 'phone'),
                ])
            if party_phone:
                ContactMechanism.write(party_phone, {
                    'value': value,
                    })
            else:
                ContactMechanism.create([{
                    'party': a.patient.name.id,
                    'type': 'phone',
                    'value': value,
                    }])

    @classmethod
    def search_rec_name(cls, name, clause):
        if clause[1].startswith('!') or clause[1].startswith('not '):
            bool_op = 'AND'
        else:
            bool_op = 'OR'
        return [bool_op,
            ('healthprof.name.name',) + tuple(clause[1:]),
            ('healthprof.name.lastname',) + tuple(clause[1:]),
            ]

    @classmethod
    def write(cls, appointments, values):
        for appointment in appointments:
            # Check if the Appointment ID is set
            if (values.get('state') or appointment.state) in ['confirmed', 'checked', 'done'] \
                and (values.get('healthprof') or appointment.healthprof) \
                and (values.get('patient') or appointment.patient) \
                and not appointment.name:
                values['name'] = cls.generate_code()
        return super(Appointment, cls).write(appointments, values)


    @staticmethod
    def default_appointment_kind():
        return 'sponteneous_appointment'

    @staticmethod
    def default_visit_type():
        return 'new'

    @staticmethod
    def default_healthprof():
        return None

    @classmethod
    def __setup__(cls):
        super(Appointment,cls).__setup__()
        #cls.visit_type.selection.append(
            #('ntcd_control','Non transmisible chronic disease'),
            #)
        #cls.visit_type.selection.append(
            #('pregnancy_control','Pregnancy Control'),
            #)


class PatientData(metaclass=PoolMeta):
    'Patient'
    __name__ = 'gnuhealth.patient'

    last_appointment= fields.Function(
        fields.DateTime('Last date',help='Get the last appointment confirmed, checked in or done'),
        'get_last_appointment',
        searcher='search_last_appointment')    
    has_appointments = fields.Function(
        fields.Boolean('Has appointments',
                       help='Checked if the patient has any appointment'),
        'get_has_appointments',searcher='search_has_appointments')

    def get_last_appointment(self,name):
        '''Brings the last appointment date'''
        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        Date = pool.get('ir.date')
        dt_today = datetime.combine(Date.today(),time())
        appointment = Appointment.search([
                ('patient','=',self.id),
                ('state','in',['checked_in','confirmed','done']),
                ('appointment_date','<=',dt_today)
                ])
        if appointment:
            return max([x.appointment_date for x in appointment])
        return None

    def get_has_appointments(self, name):
        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        appointment = Appointment.search([('patient','=',self.id)])
        if len(appointment)!= 0:
            return True
        return False

    @classmethod
    def search_has_appointments(cls, name, clause):
        '''Brings all patients that has any appointment'''
        transaction = Transaction()
        connection = transaction.connection
        cursor = connection.cursor()
        _, operator,operand1  = clause

        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        Patient = pool.get('gnuhealth.patient')
        Date = pool.get('ir.date')

        appointment = Appointment.__table__()
        patient = Patient.__table__()

        Operator = fields.SQL_OPERATORS[operator]
        query0 = appointment.select(appointment.patient)
        cursor.execute(*query0)
        result0 = cursor.fetchall()
        if operand1 == True:
            return [('id','in',[x[0] for x in result0])]
        if operand1 == False:
            return [('id','not in',[x[0] for x in result0])]

    @classmethod
    def search_last_appointment(cls, name, clause):
        '''Brings all patients that has checked_in or done appointment 
        state last appointment during a period'''
        transaction = Transaction()
        connection = transaction.connection
        cursor = connection.cursor()
        _, operator,operand1  = clause

        pool = Pool()
        Appointment = pool.get('gnuhealth.appointment')
        Patient = pool.get('gnuhealth.patient')
        Date = pool.get('ir.date')

        appointment = Appointment.__table__()
        patient = Patient.__table__()

        result1 = []
        if operator:
            Operator = fields.SQL_OPERATORS[operator]
            query0 = appointment.select(appointment.patient,
                    where= (Operator(appointment.appointment_date,operand1))&
                           ((appointment.state=='checked_in')|
                           (appointment.state=='done')|
                           (appointment.state=='confirmed')))
            cursor.execute(*query0)
            result0 = cursor.fetchall()

            result1 = []
            if operator == '<' or operator == '<=' and len(result0)!=0:
                query1 = appointment.select(appointment.patient,
                        where= (appointment.appointment_date > operand1)&
                                ((appointment.state=='checked_in')|
                                (appointment.state=='done')|
                                (appointment.state=='confirmed')))
                cursor.execute(*query1)
                result1 = cursor.fetchall()
        return [('id','in',[x[0] for x in result0 if x not in result1])]



class HealthProfessional(metaclass = PoolMeta):
    'Health Professional'
    __name__ = 'gnuhealth.healthprofessional'

    is_doctor = fields.Boolean("Is a doctor?", 
                               help=u"Check if it is a doctor")    
    time_start = fields.Time('Hora de Inicio', format='%H:%M')
    time_end = fields.Time('Hora de Fin', format='%H:%M')
    appointment_minutes = fields.Integer('Minutos entre entre citas')
    monday = fields.Boolean('Lunes')
    tuesday = fields.Boolean('Martes')
    wednesday = fields.Boolean(u'Miércoles')
    thursday = fields.Boolean('Jueves')
    friday = fields.Boolean('Viernes')
    saturday = fields.Boolean(u'Sábado')
    sunday = fields.Boolean('Domingo')
    daily_appointment_quantity = fields.Integer(
                                u"Cantidad de turnos por día",
                                help="Cantidad de turnos a otorgar")

    @fields.depends('appointment_minutes', 'time_end', 'time_start',
                    'daily_appointment_quantity')
    def on_change_with_daily_appointment_quantity(self):
        # Return the quantity of appointment per day
        if self.appointment_minutes and self.time_end and self.time_start and not self.daily_appointment_quantity:
            delta_hours = self.time_end.hour - self.time_start.hour
            delta_minutes = self.time_end.minute - self.time_start.minute
            delta_time = (delta_hours*60+delta_minutes) if delta_hours>0 else 0
            appointment_quantity = int((delta_time)/self.appointment_minutes)
            return appointment_quantity
        return self.daily_appointment_quantity

    @fields.depends('daily_appointment_quantity', 'time_end', 'time_start',
                    'appointment_minutes')
    def on_change_with_appointment_minutes(self):
        # Return the time of appointment per day
        if self.daily_appointment_quantity and self.time_end and self.time_start and not self.appointment_minutes:
            delta_hours = self.time_end.hour - self.time_start.hour
            delta_minutes = self.time_end.minute - self.time_start.minute
            delta_time = (delta_hours*60+delta_minutes) if delta_hours>0 else 0
            appointment_minutes = int((delta_time)/self.daily_appointment_quantity)
            return appointment_minutes
        return self.appointment_minutes
