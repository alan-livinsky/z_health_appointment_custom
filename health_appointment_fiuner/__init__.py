# This file is part of Health appointment  FIUNER module for GNU Health.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import health_appointment_fiuner

from .report import appointment_diary_report
from .report import appointment_report
from .report import daily_report
from .report import print_healthprof_patient_load_report

from .wizard import create_diary_appointment_report
from .wizard import wizard_health_calendar
from .wizard import wizard_health_daily_appointment
from .wizard import wizard_appointment_patient
from .wizard import wizard_create_appointment_report
from .wizard import print_healthprof_patient_load

def register():
    Pool.register(
        health_appointment_fiuner.PatientData,
        health_appointment_fiuner.Appointment,
        health_appointment_fiuner.HealthProfessional,
        create_diary_appointment_report.CreateDiaryAppointmentReportStart,
        wizard_create_appointment_report.AppointmentReportStart,
        wizard_health_calendar.CreateAppointmentStart,
        wizard_health_daily_appointment.PrintDailyAppointmentStart,
        print_healthprof_patient_load.PrintHealthProfPatientLoadStart,
        module='health_appointment_fiuner', type_='model')
    Pool.register(
        create_diary_appointment_report.CreateDiaryAppointmentReportWizard,
        wizard_create_appointment_report.AppointmentReportWizard,
        wizard_health_calendar.CreateAppointment,
        wizard_health_daily_appointment.PrintDailyAppointment,
        wizard_appointment_patient.OpenAppointmentPatient,
        print_healthprof_patient_load.PrintHealthProfPatientLoadWizard,
        module='health_appointment_fiuner', type_='wizard')
    Pool.register(
        appointment_diary_report.AppointmentDiaryReport,
        appointment_report.AppointmentReport,
        daily_report.ReportAppointmentDaily,
        print_healthprof_patient_load_report.PrintHealthProfPatientLoadReport,
        module='health_appointment_fiuner', type_='report')

