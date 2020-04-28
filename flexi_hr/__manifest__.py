# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Flexi HR',
    'category': 'HR',
    'description': """
                   Flexi HR provides a complete solution for services related to Human Resources and it's relevant perspectives.
                 """,
    'summary': 'Manage Employee Loan, payroll, recruitment processes, employee contracts, employee attendance, employee timesheet, mass leave allocation and leave management.',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 0.00,
    'currency': 'EUR',
    'depends': ['base', 'stock', 'account', 'account_invoicing',
                'hr_payroll', 'hr', 'hr_attendance',
                'hr_contract', 'hr_recruitment', 'project', 'hr_timesheet',
                ],
    'images': ['static/description/icon.png'],
    'data': [
        
        'hr_payroll/hr_payroll_data.xml',
        'hr_payroll/hr_payroll_view.xml',
        'loan/report/report.xml',
        'loan/data/loan_data.xml',
        'loan/views/loan_type_view.xml',
        'loan/views/loan_application_view.xml',
        'loan/wizard/loan_calc_view.xml',
        'loan/views/loan_setting_view.xml',
        'loan/wizard/wizard_loan_reject_view.xml',
        'loan/report/report_loan_summary.xml',
        'loan/report/report_loan_contract.xml',
        'loan/views/loan_prepayment_view.xml',
        'loan/views/loan_advance_payment_view.xml',
        'loan/views/loan_adjustment_view.xml',
        'loan/data/hr_aces_action_rule_view.xml',
        'loan/data/mail_template_view.xml',
        'loan/security/loan_security.xml',

        # Employee Checklist
        'checklist/views/checklist_setting_view.xml',
        'checklist/wizard/product_allocation_wiz_view.xml',
        'checklist/views/employee_document_view.xml',
        'checklist/views/employee_product_line_view.xml',
        'checklist/views/employee_entry_view.xml',
        'checklist/wizard/entry_product_wiz_view.xml',
        'checklist/views/employee_exit_view.xml',
        'checklist/wizard/disburse_amt_wiz_view.xml',
        'checklist/wizard/reason_cancel_view.xml',
        'checklist/views/hr_employee_view.xml',
        'checklist/views/employee_checklist_data.xml',
        'checklist/views/stock_picking_view.xml',
        'checklist/views/employee_checklist_template.xml',
        
        # HR Recruitment
        'hr_recruitment/hr_recruitment_view.xml',
        'hr_recruitment/create_employee_view.xml',
        'calendar/calendar_views.xml',
        
        # overtime
        'overtime/views/hr_employee_view.xml',
        'overtime/views/account_analytic_line_view.xml',
        
        # Event
        'event/views/event_data.xml',
        'event/views/employee_event_track_view.xml',
        'event/views/employee_event_participant_view.xml',
        'event/views/employee_event_view.xml',
        'event/wizard/employee_event_attendance_view.xml',
        'event/views/hr_employee_view.xml',
        'event/wizard/wizard_employee_event_view.xml',
        'event/views/ir_cron_data.xml',
        
        # Advance Salary Request
        'advance_salary/views/advance_salary_setting_view.xml',
        'advance_salary/views/report.xml',
        'advance_salary/views/hr_adv_salary_req_data.xml',
        'advance_salary/views/hr_adv_salary_req_view.xml',
        'advance_salary/views/hr_employee_view.xml',
        'advance_salary/views/account_move_view.xml',
        'advance_salary/views/reject_reason_view.xml',
        'advance_salary/views/advance_salary_req_template.xml',
        'advance_salary/views/disburse_amt_wiz_view.xml',
        'advance_salary/views/summary_wiz_view.xml',
        'advance_salary/views/template_summary_wiz.xml',
        'advance_salary/security/security_view.xml',
        'advance_salary/security/ir.model.access.csv',
        
        #Leave
        'leaves/data/leave_data.xml',
        'leaves/views/hr_public_holiday_view.xml',
        'leaves/views/weekly_off_group_view.xml',
        'leaves/views/leave_setting_view.xml',
        'leaves/views/hr_holidays_view.xml',
        'leaves/wizard/mass_leave_application.xml',
        'leaves/views/hr_employee_view.xml',
#         'leaves/wizard/leave_mass_allocation_view.xml',

        # attendance
        'attendance/res_config_view.xml',

        # Dynamic Payslip
        'dynamic_payslip/views/wizard_dynamic_payslip_view.xml',
        'dynamic_payslip/payslip_reports.xml', 
        'dynamic_payslip/security/ir.model.access.csv',
        'dynamic_payslip/views/dynamic_payslip_report.xml',
        'dynamic_payslip/data/design_data.xml',

        #leave encashment
        'leave_encash/security/leave_security.xml',
         'leave_encash/views/hr_job_views.xml',
         'leave_encash/wizard/leave_encash_process_views.xml',
         'leave_encash/views/leave_config_setting_views.xml',
         'leave_encash/views/leave_encash_views.xml',
         'leave_encash/views/hr_payroll_views.xml',
         'leave_encash/views/hr_payroll_data.xml',
         'leave_encash/views/report.xml',
         'leave_encash/wizard/leave_encash_report_wizard.xml',
         'leave_encash/report/leave_encash_report.xml',
         'leave_encash/security/ir.model.access.csv',
        
        'security/ir.model.access.csv',
    ],
    'demo': [
        'data/flexi_hr_demo.xml'
    ],
    'external_dependencies': {
        'python': [
            'numpy'
        ],
    },
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
