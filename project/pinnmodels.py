# \osc\project\pinnmodels.py
# This is a hand-generated Django model module.
#   * 
#   * Made sure each model has one field with primary_key=True
#   * Made sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Kept `managed = False` lines if you wish to not  allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User

# This view uses the Pinnacle location table and includes locations added by ITS staff
#  as well as the official builfing codes from MPathways


class UmBillInputApiV(models.Model):
     um_bill_input_id = models.IntegerField(primary_key=True)
     data_source = models.CharField(max_length=50)
     assign_date = models.CharField(max_length=20)
     unique_identifier = models.CharField(max_length=200)
     short_code = models.CharField(max_length=100)
     charge_identifier = models.CharField(max_length=200)
     quantity_vouchered = models.IntegerField()
     invoice_id = models.CharField(max_length=100)
     m_uniqname = models.CharField(max_length=100)
     voucher_comment = models.CharField(max_length=100)
     load_date = models.DateField()
     date_processed = models.DateField(null=True)
     full_input_record = models.CharField(max_length=1000)
     bill_input_file_id = models.IntegerField()
     total_amount = models.DecimalField(max_digits=13, decimal_places=2)

     class Meta:
          managed = False
          db_table = 'PS_RATING\".\"um_bill_input_api_v'

     def __str__(self):
          return self.um_bill_input_id

class UmOSCBuildingV(models.Model):
   building_code = models.CharField(max_length=15, primary_key=True)
   building_name = models.CharField(max_length=100,null=True) 

   class Meta:
        managed = False
        ordering = ('building_code', )
        db_table = 'PINN_CUSTOM\".\"um_osc_location_profile_v'

   def __str__(self):
        return self.building_name

class UmOscDeptProfileV(models.Model):
   deptid = models.CharField(max_length=15, primary_key=True)
   dept_eff_status = models.CharField(max_length=1,null=True) 
   dept_name = models.CharField(max_length=50,null=True)
   dept_grp = models.CharField(max_length=20,null=True)
   dept_summary_subscriber_id = models.CharField(max_length=7,null=True)
   dept_mgr = models.CharField(max_length=50,null=True)
   dept_mgr_uniqname = models.CharField(max_length=8,null=True)
   dept_mgr_phone = models.CharField(max_length=24,null=True)
   dept_default_exp_chartfield = models.CharField(max_length=100,null=True)
   dept_occ_chartfield = models.CharField(max_length=100,null=True)
   dept_mrc_chartfield = models.CharField(max_length=100,null=True)
   dept_toll_chartfield = models.CharField(max_length=100,null=True)
   dept_local_chartfield = models.CharField(max_length=100,null=True)
   dept_other_chartfield = models.CharField(max_length=100,null=True)
   
   class Meta:
        managed = False
        ordering = ('dept_name', )
        db_table = 'PINN_CUSTOM\".\"um_osc_dept_profile_v'

   def __str__(self):
        return self.dept_name

class UmOscAllServLocV(models.Model):
   location_id = models.IntegerField(primary_key=True)
   building_code =  models.CharField(max_length=10, blank=True, null=True)
   building_name =  models.CharField(max_length=25, blank=True, null=True)
   floor_name =  models.CharField(max_length=18, blank=True, null=True)
   room_name =  models.CharField(max_length=18, blank=True, null=True)
   jack_name =  models.CharField(max_length=18, blank=True, null=True)
   location_display =  models.CharField(max_length=114, blank=True, null=True)  
   cable_path_id = models.IntegerField(null=True)
   active = models.IntegerField(1)
   is_assigned = models.IntegerField()
   on_open_wo = models.IntegerField()
    
   class Meta: 
        managed = False
        ordering = ('building_name', 'floor_name', 'room_name', 'jack_name')
        db_table = 'PINN_CUSTOM\".\"um_osc_all_serv_loc_v'

   def __str__(self):
        return self.location_display

class UmOscChartfieldV(models.Model):
   short_code = models.CharField(max_length=10, blank=True, null=True)
   chartfield =  models.CharField(max_length=100,primary_key=True)
   fund =  models.CharField(max_length=30, blank=True, null=True)
   fund_desc =  models.CharField(max_length=30, blank=True, null=True)
   fund_eff_status =  models.CharField(max_length=1, blank=True, null=True)
   deptid =  models.CharField(max_length=30, blank=True, null=True)
   dept_desc =  models.CharField(max_length=30, blank=True, null=True)
   dept_eff_status =  models.CharField(max_length=1, blank=True, null=True)
   program =  models.CharField(max_length=30, blank=True, null=True)
   program_desc =  models.CharField(max_length=30, blank=True, null=True)
   program_eff_status =  models.CharField(max_length=1, blank=True, null=True)
   class_code =  models.CharField(max_length=30, blank=True, null=True)
   class_desc =  models.CharField(max_length=30, blank=True, null=True)
   class_eff_status =  models.CharField(max_length=1, blank=True, null=True)
   project_grant =  models.CharField(max_length=30, blank=True, null=True)
   project_grant_desc =  models.CharField(max_length=225, blank=True, null=True)
   project_grant_eff_status =  models.CharField(max_length=3, blank=True, null=True)
   active =  models.CharField(max_length=1, blank=True, null=True)
   dept_default =  models.CharField(max_length=1, blank=True, null=True)
   used_last_month =  models.CharField(max_length=1, blank=True, null=True)
   used_within_year =  models.CharField(max_length=1, blank=True, null=True)




    
   class Meta:
        managed = False
        ordering = ('deptid', 'chartfield')
        db_table = 'PINN_CUSTOM\".\"um_osc_chartfield_v'

   def __str__(self):
        return self.chartfield

class UmOscServiceProfileV(models.Model):
   deptid =  models.CharField(max_length=15, blank=True, null=True)
   service_number = models.CharField(max_length=60,primary_key=True)
   service_status_code = models.CharField(max_length=15, blank=True, null=True)
   service_type = models.CharField(max_length=20, blank=True, null=True)
   subscriber_id = models.CharField(max_length=7,null=True)
   subscriber_status = models.CharField(max_length=20, null=True)
   user_defined_id = models.CharField(max_length=20, null=True)
   start_date =  models.DateField(null=True)
   end_date =  models.DateField(null=True)
   location_id = models.IntegerField(null=True)
   building_code =  models.CharField(max_length=10, blank=True, null=True)
   building_name =  models.CharField(max_length=25, blank=True, null=True)
   floor_name =  models.CharField(max_length=18, blank=True, null=True)
   room_name =  models.CharField(max_length=18, blank=True, null=True)
   jack_name =  models.CharField(max_length=30, blank=True, null=True)
   cable_path_id =  models.IntegerField(null=True)
   dept_default_exp_chartfield = models.CharField(max_length=100,null=True)
   occ_exp_chartfield = models.CharField(max_length=100,null=True)
   mrc_exp_chartfield = models.CharField(max_length=100,null=True)
   toll_exp_chartfield = models.CharField(max_length=100,null=True)
   local_exp_chartfield = models.CharField(max_length=100,null=True)
   other_exp_chartfield = models.CharField(max_length=100,null=True)
   

    
   class Meta:
        managed = False 
        ordering = ('deptid', 'service_number')    
        db_table = 'PINN_CUSTOM\".\"um_osc_service_profile_v'    

   def __str__(self):
        return self.service_number

class UmOscPreorderApiAbstract(models.Model):
   pre_order_id =  models.BigIntegerField( null=True)
   category_code =  models.CharField(max_length=4, blank=True, null=True)
   wo_type_category_id =  models.BooleanField(null=True)
   wo_type_category_name =  models.CharField(max_length=240, blank=True, null=True)
   pre_order_number =  models.BigIntegerField(null=True)
   pre_order_issue =  models.BigIntegerField(null=True)
   pre_order_converted_date =  models.DateField(null=True)
   pre_order_converted_by =  models.CharField(max_length=400, blank=True, null=True)
   pre_order_number_display =  models.CharField(max_length=88, blank=True, null=True)
   wo_type_code =  models.CharField(max_length=8, blank=True, null=True)
   wo_type_name =  models.CharField(max_length=80, blank=True, null=True)
   wo_number =  models.IntegerField(7, null=True)
   wo_issue =  models.IntegerField(3, null=True)
   wo_number_display =  models.CharField(max_length=56, blank=True, null=True)
   priority_code =  models.CharField(max_length=4, blank=True, null=True)
   priority_name =  models.CharField(max_length=240, blank=True, null=True)
   status_code =  models.CharField(max_length=4, blank=True, null=True)
   status_name =  models.CharField(max_length=240, blank=True, null=True)
   action_code =  models.CharField(max_length=4, blank=True, null=True)
   action_name =  models.CharField(max_length=240, blank=True, null=True)
   suspend_restore_code =  models.CharField(max_length=4, blank=True, null=True)
   suspend_restore_name =  models.CharField(max_length=80, blank=True, null=True)
   comment_text =  models.CharField(max_length=4000, blank=True, null=True)
   department_number =  models.CharField(max_length=15, blank=True, null=True)
   department_id =  models.IntegerField(9, null=True)
   department_name =  models.CharField(max_length=200, blank=True, null=True)
   division_code =  models.CharField(max_length=60, blank=True, null=True)
   division_name =  models.CharField(max_length=200, blank=True, null=True)
   contact_phone_number =  models.CharField(max_length=200, blank=True, null=True)
   contact_last_name =  models.CharField(max_length=200, blank=True, null=True)
   contact_first_name =  models.CharField(max_length=200, blank=True, null=True)
   form_display_contact_name =  models.CharField(max_length=600, blank=True, null=True)
   contact_email_address =  models.CharField(max_length=1280, blank=True, null=True)
   contact_id =  models.BigIntegerField( null=True)
   project_type_code =  models.CharField(max_length=12, blank=True, null=True)
   project_name =  models.CharField(max_length=200, blank=True, null=True)
   project_number =  models.BigIntegerField( null=True)
   project_id =  models.IntegerField(9, null=True)
   project_display =  models.CharField(max_length=384, blank=True, null=True)
   project_code_display =  models.CharField(max_length=80, blank=True, null=True)
   assigned_labor_code =  models.CharField(max_length=36, blank=True, null=True)
   assigned_labor_name_display =  models.CharField(max_length=508, blank=True, null=True)
   work_status_id =  models.BigIntegerField( null=True)
   work_status_name =  models.CharField(max_length=284, blank=True, null=True)
   approval_required =  models.BooleanField(null=True)
   approval_status_code =  models.CharField(max_length=4, blank=True, null=True)
   approval_status_name =  models.CharField(max_length=240, blank=True, null=True)
   approval_date =  models.DateField(null=True)
   approval_user =  models.CharField(max_length=400, blank=True, null=True)
   approval_est_expires_on =  models.DateField(null=True)
   estimated_recurring_amount =   models.DecimalField(decimal_places=4, max_digits=19,  null=True)
   estimated_one_time_amount =   models.DecimalField(decimal_places=4, max_digits=19,  null=True)
   problem_code =  models.CharField(max_length=12, blank=True, null=True)
   problem_display =  models.CharField(max_length=168, blank=True, null=True)
   resolution_code =  models.CharField(max_length=12, blank=True, null=True)
   resolution_display =  models.CharField(max_length=168, blank=True, null=True)
   trouble_reported_date =  models.DateField(null=True)
   actual_respond_date =  models.DateField(null=True)
   actual_respond_user =  models.CharField(max_length=400, blank=True, null=True)
   actual_resolved_user =  models.CharField(max_length=400, blank=True, null=True)
   trouble_cleared_date =  models.DateField(null=True)
   actual_resolved_date =  models.DateField(null=True)
   due_date =  models.DateField(null=True)
   receive_date =  models.DateField(null=True)
   created_user =  models.CharField(max_length=400, blank=True, null=True)
   created_date =  models.DateField(null=True)
   last_update_user =  models.CharField(max_length=400, blank=True, null=True)
   last_update_date =  models.DateField(null=True)
   estimated_start_date =  models.DateField(null=True)
   estimated_completion_date =  models.DateField(null=True)
   actual_start_date =  models.DateField(null=True)
   actual_fulfilled_user =  models.CharField(max_length=400, blank=True, null=True)
   actual_completion_date =  models.DateField(null=True)
   actual_fulfilled_date =  models.DateField(null=True)
   closed_user =  models.CharField(max_length=400, blank=True, null=True)
   closed_date =  models.DateField(null=True)
   inspection_date =  models.DateField(null=True)
   inspection_code =  models.CharField(max_length=32, blank=True, null=True)
   cust_satisfaction_level =  models.CharField(max_length=20, blank=True, null=True)
   requisition_number =  models.CharField(max_length=48, blank=True, null=True)
   note_key =  models.BigIntegerField(null=True)
   new_subscriber =  models.BooleanField(null=True)
   subscriber_id =  models.CharField(max_length=28, blank=True, null=True)
   subscriber_user_def_id =  models.CharField(max_length=80, blank=True, null=True)
   subscriber_first_name =  models.CharField(max_length=200, blank=True, null=True)
   subscriber_mi =  models.CharField(max_length=4, blank=True, null=True)
   subscriber_last_name =  models.CharField(max_length=200, blank=True, null=True)
   form_display_subscriber_name =  models.CharField(max_length=420, blank=True, null=True)
   list_display_subscriber_name =  models.CharField(max_length=420, blank=True, null=True)
   subscriber_status_code =  models.CharField(max_length=80, blank=True, null=True)
   subscriber_group_name =  models.CharField(max_length=80, blank=True, null=True)
   subscriber_group_id =  models.BigIntegerField( null=True)
   hierarchy_level_id =  models.IntegerField(9, null=True)
   hierarchy_level_code =  models.CharField(max_length=200, blank=True, null=True)
   hierarchy_level_name =  models.CharField(max_length=400, blank=True, null=True)
   hierarchy_path =  models.CharField(max_length=4000, blank=True, null=True)
   assign_start_date =  models.DateField(null=True)
   assign_end_date =  models.DateField(null=True)
   default_recurring_expense_acct =  models.CharField(max_length=400, blank=True, null=True)
   recurring_expense_acct_name =  models.CharField(max_length=400, blank=True, null=True)
   default_one_time_expense_acct =  models.CharField(max_length=400, blank=True, null=True)
   one_time_expense_acct_name =  models.CharField(max_length=400, blank=True, null=True)
   current_service_type_id =  models.BigIntegerField( null=True)
   new_service_type_id =  models.BigIntegerField( null=True)
   current_service_type_code =  models.CharField(max_length=80, blank=True, null=True)
   orig_service_type_code =  models.CharField(max_length=80, blank=True, null=True)
   new_service_type_code =  models.CharField(max_length=80, blank=True, null=True)
   current_service_id =  models.BigIntegerField( null=True)
   current_service_number =  models.CharField(max_length=240, blank=True, null=True)
   current_switch_id =  models.BigIntegerField( null=True)
   current_switch_name =  models.CharField(max_length=120, blank=True, null=True)
   current_svc_loc_id =  models.BigIntegerField( null=True)
   current_svc_loc_bl_id =  models.IntegerField(9, null=True)
   current_svc_loc_bl_code =  models.CharField(max_length=40, blank=True, null=True)
   current_svc_loc_bl_name =  models.CharField(max_length=100, blank=True, null=True)
   current_svc_loc_bl_address =  models.CharField(max_length=3284, blank=True, null=True)
   current_svc_loc_floor =  models.CharField(max_length=72, blank=True, null=True)
   current_svc_loc_room =  models.CharField(max_length=72, blank=True, null=True)
   current_svc_loc_jack =  models.CharField(max_length=120, blank=True, null=True)
   current_svc_loc_path_id =  models.BigIntegerField( null=True)
   current_svc_loc_display =  models.CharField(max_length=456, blank=True, null=True)
   new_service =  models.BooleanField(null=True)
   new_service_id =  models.BigIntegerField( null=True)
   new_service_number =  models.CharField(max_length=240, blank=True, null=True)
   switch_name =  models.CharField(max_length=120, blank=True, null=True)
   current_private_number =  models.CharField(max_length=240, blank=True, null=True)
   new_private_number =  models.CharField(max_length=240, blank=True, null=True)
   new_svc_loc_id =  models.BigIntegerField( null=True)
   new_svc_loc_bl_id =  models.IntegerField(9, null=True)
   new_svc_loc_bl_code =  models.CharField(max_length=40, blank=True, null=True)
   new_svc_loc_bl_name =  models.CharField(max_length=100, blank=True, null=True)
   new_svc_loc_bl_address =  models.CharField(max_length=3284, blank=True, null=True)
   new_svc_loc_floor =  models.CharField(max_length=72, blank=True, null=True)
   new_svc_loc_room =  models.CharField(max_length=72, blank=True, null=True)
   new_svc_loc_jack =  models.CharField(max_length=120, blank=True, null=True)
   new_svc_loc_path_id =  models.BigIntegerField( null=True)
   new_svc_loc_display =  models.CharField(max_length=456, blank=True, null=True)
   svc_loc_display =  models.CharField(max_length=456, blank=True, null=True)
   new_location =  models.BooleanField(null=True)
   created_loc_id =  models.BigIntegerField( null=True)
   created_path_id =  models.BigIntegerField( null=True)
   nena_create_date =  models.DateField(null=True)
   signoff_status_id =  models.IntegerField(9, null=True)
   signoff_status_name =  models.CharField(max_length=240, blank=True, null=True)
   signoff_required =  models.BooleanField(null=True)
   signoff_date =  models.DateField(null=True)
   signoff_sent_date =  models.DateField(null=True)
   signoff_reminder_sent_dt =  models.DateField(null=True)
   signoff_expire_date =  models.DateField(null=True)
   signoff_method_id =  models.BigIntegerField( null=True)
   signoff_method_name =  models.CharField(max_length=240, blank=True, null=True)
   signoff_timeout =  models.BigIntegerField( null=True)
   survey_inst_id =  models.IntegerField(9, null=True)
   sla_id =  models.IntegerField(9, null=True)
   sla_code =  models.CharField(max_length=200, blank=True, null=True)
   sla_name =  models.CharField(max_length=400, blank=True, null=True)
   sla_severity_id =  models.IntegerField(9, null=True)
   sla_severity_code =  models.CharField(max_length=200, blank=True, null=True)
   sla_severity_name =  models.CharField(max_length=400, blank=True, null=True)
   sla_urgency_id =  models.IntegerField(9, null=True)
   sla_urgency_sequence =  models.BigIntegerField( null=True)
   sla_respond_by_date =  models.DateField(null=True)
   sla_respond_remind_dt =  models.DateField(null=True)
   sla_resolve_by_date =  models.DateField(null=True)
   sla_resolve_remind_date =  models.DateField(null=True)
   sla_urgency_remind_date =  models.DateField(null=True)
   sla_start_date =  models.DateField(null=True)
   sla_escalation_date =  models.DateField(null=True)
   sla_escalation_on_hold =  models.BooleanField(null=True)
   sla_escalation_restart =  models.DateField(null=True)
   sla_respond_missed_dt =  models.BooleanField(null=True)
   sla_resolve_missed_dt =  models.BooleanField(null=True)
   wo_step_id =  models.IntegerField(9, null=True)
   wo_step_code =  models.CharField(max_length=200, blank=True, null=True)
   wo_step_name =  models.CharField(max_length=400, blank=True, null=True)
   quick_incident =  models.BooleanField(null=True)
   script =  models.CharField(max_length=4000, blank=True, null=True)
   add_info_text_1 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="Estimated Hours")
   add_info_text_2 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="Area Of Campus")
   add_info_text_3 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="OSC Order Number")
   add_info_text_4 =  models.CharField(max_length=512, primary_key=True, verbose_name="OSC Order Item Number")
   add_info_text_5 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="V.O.I.P WO")
   add_info_text_6 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="# of Data Act")
   add_info_text_7 =  models.CharField(max_length=512, blank=True, null=True)
   add_info_text_8 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="Set Type")
   add_info_text_9 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="MAC Address")
   add_info_text_10 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="Serial Number")
   add_info_text_11 =  models.CharField(max_length=512, blank=True, null=True)
   add_info_text_12 =  models.CharField(max_length=512, blank=True, null=True, verbose_name="Transition Ord #")
   add_info_text_13 =  models.CharField(max_length=512, blank=True, null=True)
   add_info_text_14 =  models.CharField(max_length=512, blank=True, null=True)
   add_info_text_15 =  models.CharField(max_length=512, blank=True, null=True)
   add_info_text_16 =  models.CharField(max_length=512, blank=True, null=True)
   add_info_checkbox_1 =  models.BooleanField(null=True, verbose_name="Draft Comp-D")
   add_info_checkbox_2 =  models.BooleanField(null=True, verbose_name="Asbuilt Recv'd-D")
   add_info_checkbox_3 =  models.BooleanField(null=True, verbose_name="Asbuilt Compl-D")
   add_info_checkbox_4 =  models.BooleanField(null=True)
   add_info_checkbox_5 =  models.BooleanField(null=True, verbose_name="Asbuilt/Prints-F")
   add_info_checkbox_6 =  models.BooleanField(null=True, verbose_name="Closeout Compl-F")
   add_info_checkbox_7 =  models.BooleanField(null=True, verbose_name="Asbuilt/Prints Received-A")
   add_info_checkbox_8 =  models.BooleanField(null=True, verbose_name="Assignments Complete-A")
   add_info_checkbox_9 =  models.BooleanField(null=True)
   add_info_checkbox_10 =  models.BooleanField(null=True)
   add_info_date_1 =  models.DateField(null=True, verbose_name="Closed Date")
   add_info_date_2 =  models.DateField(null=True, verbose_name="Complete by FSU")
   add_info_date_3 =  models.DateField(null=True, verbose_name="Customer Requested Due Date")
   add_info_date_4 =  models.DateField(null=True)
   add_info_date_5 =  models.DateField(null=True)
   add_info_date_6 =  models.DateField(null=True)
   add_info_date_7 =  models.DateField(null=True)
   add_info_date_8 =  models.DateField(null=True)
   add_info_date_9 =  models.DateField(null=True)
   add_info_date_10 =  models.DateField(null=True)
   add_info_number_1 =  models.BigIntegerField( null=True, verbose_name="Estimate")
   add_info_number_2 =  models.BigIntegerField( null=True, verbose_name="Final Estimate")
   add_info_number_3 =  models.BigIntegerField( null=True)
   add_info_number_4 =  models.BigIntegerField( null=True)
   add_info_number_5 =  models.BigIntegerField( null=True)
   add_info_number_6 =  models.BigIntegerField( null=True)
   add_info_number_7 =  models.BigIntegerField( null=True)
   add_info_number_8 =  models.BigIntegerField( null=True)
   add_info_number_9 =  models.BigIntegerField( null=True)
   add_info_number_10 =  models.BigIntegerField( null=True)
   add_info_list_value_id_1 =  models.IntegerField(null=True, verbose_name="Building")
   add_info_list_value_code_1 =  models.CharField(max_length=200, blank=True, null=True, verbose_name="Bill Error Codes")
   add_info_list_value_name_1 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_2 =  models.IntegerField(9, null=True)
   add_info_list_value_code_2 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_2 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_3 =  models.IntegerField(9, null=True)
   add_info_list_value_code_3 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_3 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_4 =  models.IntegerField(9, null=True)
   add_info_list_value_code_4 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_4 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_5 =  models.IntegerField(9, null=True)
   add_info_list_value_code_5 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_5 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_6 =  models.IntegerField(9, null=True)
   add_info_list_value_code_6 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_6 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_7 =  models.IntegerField(9, null=True)
   add_info_list_value_code_7 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_7 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_8 =  models.IntegerField(9, null=True)
   add_info_list_value_code_8 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_8 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_9 =  models.IntegerField(9, null=True)
   add_info_list_value_code_9 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_9 =  models.CharField(max_length=400, blank=True, null=True)
   add_info_list_value_id_10 =  models.IntegerField(9, null=True)
   add_info_list_value_code_10 =  models.CharField(max_length=200, blank=True, null=True)
   add_info_list_value_name_10 =  models.CharField(max_length=400, blank=True, null=True)
   originating_source_id =  models.IntegerField(1, null=True)
   originating_source_name =  models.CharField(max_length=80, blank=True, null=True)
   add_info_values_id =  models.BigIntegerField(null=False)
   add_info_row_defn_id =  models.IntegerField(9, null=False)
   switch_id =  models.BigIntegerField(null=True)
   svc_bill_description =  models.CharField(max_length=400, blank=True, null=True)
   sub_id_to_swap_with =  models.CharField(max_length=28, blank=True, null=True)
   svc_id_to_swap_with =  models.BigIntegerField(null=True)
   loc_id_to_swap_with =  models.BigIntegerField(null=True)
   move_svc_chars =  models.BooleanField(null=True)
   move_feat_items =  models.BooleanField(null=True)
   move_inventory =  models.BooleanField(null=True)
   subscriber_only_swap =  models.BooleanField(null=True)
   note_subject =  models.CharField(max_length=1020, blank=True, null=True)
   note_text =  models.CharField(max_length=4000, blank=True, null=True)
   wo_id_2 =  models.BigIntegerField( null=True)
   subscriber_email =  models.CharField(max_length=1280, blank=True, null=True)

   class Meta:
        abstract = True 

class UmOscPreorderApiV(UmOscPreorderApiAbstract):
   pass

   class Meta:
        managed = False 
        ordering = ('add_info_text_3', 'pre_order_number', 'pre_order_issue')    
        db_table = 'PINN_CUSTOM\".\"um_osc_preorder_api_v'    

   def __str__(self):
        return self.pre_order_number_display


class UmCurrentDeptManagersV(models.Model):
   deptid = models.CharField(max_length=10) 
   dept_name = models.CharField(max_length=30)
   dept_status = models.CharField(max_length=1)
   dept_mgr_emplid = models.CharField(max_length=11)
   dept_mgr_name = models.CharField(max_length=50)
   dept_mgr_uniqname = models.CharField(max_length=20, primary_key=True) 
    
   class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"um_current_dept_managers_v'

class UmOscNoteProfileV(models.Model):
   note_id =  models.IntegerField(9, null=False, primary_key=True)
   note_type_id =  models.IntegerField(9, null=False)
   note_type_code =  models.CharField(max_length=120, blank=True, null=True)
   note_type_subcode =  models.CharField(max_length=120, blank=True, null=True)
   note_types_id =  models.IntegerField(9, null=False)
   note_types_code =  models.CharField(max_length=200, blank=True, null=True)
   note_types_name =  models.CharField(max_length=400, blank=True, null=True)
   accessibility =  models.BooleanField()
   accessibility_name =  models.CharField(max_length=240, blank=True, null=True)
   note_keyid_value =  models.IntegerField(9, null=True)
   note_keyid_value2 =  models.IntegerField(9, null=True)
   note_subject =  models.CharField(max_length=1020, blank=True, null=True)
   note_body = models.TextField(null=True)
   note_body_stripped =  models.CharField(max_length=4000, blank=True, null=True)
   primary_note =  models.BooleanField()
   tenant_code =  models.CharField(max_length=120, blank=True, null=True)
   note_author =  models.CharField(max_length=400, blank=True, null=True)
   note_creation_date =  models.DateField(null=True)
   last_update_user =  models.CharField(max_length=400, blank=True, null=True)
   last_update_date =  models.DateField(null=True)

   
   class Meta:
        managed = False 
        ordering = ('note_keyid_value', 'note_id')    
        db_table = 'PINN_CUSTOM\".\"um_osc_note_profile_v'    

   def __str__(self):
        return self.note_subject

        
class UmOscAttachmentApiAbstract(models.Model):      
   attachment_id =  models.IntegerField(9, null=False)
   note_id =  models.IntegerField(9, null=False)
   attachment_type_id =  models.IntegerField(9, null=False)
   attachment_type_code =  models.CharField(max_length=240, blank=True, null=True)
   attachment_type_subcode =  models.CharField(max_length=240, blank=True, null=True)
   attachment_keyid_value =  models.IntegerField(9, null=False)
   attachment_keyid_value2 =  models.IntegerField(9, null=True)
   description =  models.CharField(max_length=1020, blank=True, null=True)
   file_name =  models.CharField(max_length=1020, blank=True, null=True)
   file_size =  models.IntegerField(10, null=False)
   mime_type =  models.CharField(max_length=1020, blank=True, null=True)
   blob_content = models.BinaryField(null=True)
   tenant_code =  models.CharField(max_length=120, blank=True, null=True)
   primary_attachment =  models.BooleanField()
   last_update_user =  models.CharField(max_length=400, blank=True, null=True)
   last_update_date =  models.DateField(null=True)
   attachment_dir =  models.CharField(max_length=512, blank=True, null=True)
   attachment_guid =  models.CharField(max_length=4000, blank=True, null=True)


   class Meta:
        abstract = True
   
class UmOscAttachmentApiV(UmOscAttachmentApiAbstract):
   pass

   class Meta:
        managed = False 
        ordering = ('attachment_keyid_value', 'description')    
        db_table = 'PINN_CUSTOM\".\"um_osc_attachment_api_v'    

   def __str__(self):
        return self.description                   


class UmOscDeptUnitsReptV(models.Model):
     fiscal_yr = models.CharField(max_length=4)
     calendar_yr = models.CharField(max_length=4)
     month = models.CharField(max_length=2)
     deptid = models.CharField(max_length=6) 
     dept_descr = models.CharField(max_length=30)
     dept_grp = models.CharField(max_length=20) 
     dept_grp_descr = models.CharField(max_length=30)
     dept_grp_vp_area = models.CharField(max_length=20) 
     dept_grp_vp_area_descr = models.CharField(max_length=30)
     account = models.CharField(max_length=6) 
     account_desc = models.CharField(max_length=20)
     charge_group = models.CharField(primary_key=True, max_length=50)
     charge_code = models.CharField(max_length=50)
     description = models.CharField(max_length=100)
     unit_rate = models.CharField(max_length=40)
     quantity = models.PositiveIntegerField(null=True)
     amount = models.DecimalField(decimal_places=2, max_digits=19,  null=False)
    
     class Meta:
          managed = False
          db_table = 'PINN_CUSTOM\".\"um_osc_dept_units_rept_v'

class UmOscChartcomInitialLoadV(models.Model):
     short_code = models.CharField(max_length=10)
     fund = models.CharField(max_length=30)
     dept = models.CharField(max_length=30)
     program = models.CharField(max_length=30)
     class_code = models.CharField(max_length=30)
     project_grant = models.CharField(max_length=30)
     account_number = models.CharField(max_length=4000, primary_key=True)
     name = models.CharField(max_length=120)

     class Meta:
          managed = False
          ordering = ('dept', 'account_number')
          db_table = 'PINN_CUSTOM\".\"um_osc_chartcom_initial_load_v'


class UmOscAllActiveAcctNbrsV(models.Model):
   short_code = models.CharField(max_length=10, blank=True, null=True)
   account_number =  models.CharField(max_length=100,primary_key=True)
   fund =  models.CharField(max_length=30, blank=True, null=True)
   fund_desc =  models.CharField(max_length=30, blank=True, null=True)
   fund_eff_status =  models.CharField(max_length=1, blank=True, null=True)
   deptid =  models.CharField(max_length=30, blank=True, null=True)
   dept_desc =  models.CharField(max_length=30, blank=True, null=True)
   dept_eff_status =  models.CharField(max_length=1, blank=True, null=True)
   program =  models.CharField(max_length=30, blank=True, null=True)
   program_desc =  models.CharField(max_length=30, blank=True, null=True)
   program_eff_status =  models.CharField(max_length=1, blank=True, null=True)
   class_code =  models.CharField(max_length=30, blank=True, null=True)
   class_desc =  models.CharField(max_length=30, blank=True, null=True)
   class_eff_status =  models.CharField(max_length=1, blank=True, null=True)
   project_grant =  models.CharField(max_length=30, blank=True, null=True)
   project_grant_desc =  models.CharField(max_length=225, blank=True, null=True)
   project_grant_eff_status =  models.CharField(max_length=3, blank=True, null=True)
   active =  models.CharField(max_length=1, blank=True, null=True)

   class Meta:
        managed = False
        ordering = ('deptid', 'account_number')
        db_table = 'PINN_CUSTOM\".\"um_osc_all_active_acct_nbrs_v'

class UmOscAvailableLocsV(models.Model):
     campus_code = models.CharField(max_length=4)
     campus_desc = models.CharField(max_length=30)
     service_type = models.CharField(max_length=20)
     service_number = models.CharField(max_length=60, primary_key=True)
     status = models.CharField(max_length=15)
     service_id = models.IntegerField(9, null=False)
     location_id = models.IntegerField(9, null=False)
     path_id = models.IntegerField(9, null=False)
     building_id = models.CharField(max_length=10)
     building_name = models.CharField(max_length=25)
     floor = models.CharField(max_length=18)
     floor_desc = models.CharField(max_length=50)
     room = models.CharField(max_length=18)
     room_desc = models.CharField(max_length=50)
     jack = models.CharField(max_length=30)

     class Meta:
          managed = False
          ordering = ('service_number',)
          db_table = 'PINN_CUSTOM\".\"um_osc_available_locs_v'

class UmOscLocationsInUseV(models.Model): 
     campuscd = models.CharField(max_length=4)
     campus_desc = models.CharField(max_length=30)
     service_type = models.CharField(max_length=20)
     service_number = models.CharField(max_length=60)   
     #service_subscrib_id = models.IntegerField(9, null=False)  
     status = models.CharField(max_length=15)
     service_id = models.IntegerField(9, null=False)
     location_id = models.IntegerField(9, null=False)
     path_id = models.IntegerField(9, null=False)
     building_id = models.CharField(max_length=10, primary_key=True)  # DEBUG
     building_name = models.CharField(max_length=25)
     floor = models.CharField(max_length=18)
     floor_desc = models.CharField(max_length=50)
     room = models.CharField(max_length=18)
     room_desc = models.CharField(max_length=50)
     jack = models.CharField(max_length=30)

     class Meta:
          managed = False
          ordering = ('building_id','floor','room','jack')
          db_table = 'PINN_CUSTOM\".\"um_osc_locations_in_use_v'

class UmOscVoipLocChangeInput(models.Model):
     uniqname = models.CharField(max_length=8) 
     service_id = models.IntegerField(9, null=False)
     service_number= models.CharField(max_length=60)
     #service_subscrib_id = models.IntegerField(9, null=False)
     old_campuscd = models.CharField(max_length=4)
     old_campus_desc = models.CharField(max_length=30)
     old_location_id = models.IntegerField(9, null=False)
     old_path_id = models.IntegerField(9, null=False)
     old_building_id = models.CharField(max_length=10)
     old_building_name = models.CharField(max_length=255)
     old_floor = models.CharField(max_length=18)
     old_floor_desc = models.CharField(max_length=50)
     old_room = models.CharField(max_length=18)
     old_room_desc = models.CharField(max_length=50)
     old_jack = models.CharField(max_length=30)
     service_id_at_new_loc = models.IntegerField(9, null=False)
     service_nbr_at_new_loc = models.CharField(max_length=60)   
     service_type_at_new_loc = models.CharField(max_length=20)
     svc_status_at_new_loc = models.CharField(max_length=15)
     new_campuscd = models.CharField(max_length=4)
     new_campus_desc = models.CharField(max_length=30)
     new_location_id = models.IntegerField(9, null=False)
     new_path_id = models.IntegerField(9, null=False)
     new_building_id = models.CharField(max_length=10)
     new_building_name = models.CharField(max_length=255)
     new_floor = models.CharField(max_length=18)
     new_floor_desc = models.CharField(max_length=50)
     new_room = models.CharField(max_length=18)
     new_room_desc = models.CharField(max_length=50)
     new_jack = models.CharField(max_length=30)
     request_no = models.IntegerField(9, null=False, primary_key=True)
     date_added = models.DateField()
     date_processed = models.DateField()
     messages = models.CharField(max_length=2000)

     class Meta:
          managed = False
          ordering = ('request_no',)
          db_table = 'PINN_CUSTOM\".\"um_osc_voip_loc_change_input'


class UmOscAcctsInUseV(models.Model):
   short_code = models.CharField(max_length=10, blank=True, null=True)
   account_number =  models.CharField(max_length=100,primary_key=True)
   fund =  models.CharField(max_length=30, blank=True, null=True)
   fund_desc =  models.CharField(max_length=30, blank=True, null=True)
   deptid =  models.CharField(max_length=30, blank=True, null=True)
   dept_desc =  models.CharField(max_length=30, blank=True, null=True)
   program =  models.CharField(max_length=30, blank=True, null=True)
   program_desc =  models.CharField(max_length=30, blank=True, null=True)
   class_code =  models.CharField(max_length=30, blank=True, null=True)
   class_desc =  models.CharField(max_length=30, blank=True, null=True)
   project_grant =  models.CharField(max_length=30, blank=True, null=True)
   project_grant_desc =  models.CharField(max_length=225, blank=True, null=True)
   active =  models.CharField(max_length=1, blank=True, null=True)

   # CAN YOU ADD A PROPERTY TO LEGACY DATABASE?
   @property
   def nickname(self):
       name = Chartcom.objects.filter(account_number=account_number)[0].name

       return name

   class Meta:
        managed = False
        ordering = ('deptid', 'account_number')
        db_table = 'PINN_CUSTOM\".\"um_osc_accts_in_use_v'

class UmOscAcctChangeInput(models.Model):
     uniqname = models.CharField(max_length=8) 
     user_defined_id = models.CharField(max_length=20)
     mrc_account_number = models.CharField(max_length=100)
     toll_account_number = models.CharField(max_length=100)
     local_account_number = models.CharField(max_length=100)
     date_added = models.DateField(null=True) # added null=True
     date_processed = models.DateField(null=True) # added null=True
     messages = models.CharField(max_length=2000)
     request_no = models.IntegerField(9, null=False, primary_key=True)

     class Meta:
          managed = False
          ordering = ('request_no',)
          db_table = 'PINN_CUSTOM\".\"um_osc_acct_change_input'

class UmOscAcctSubscribersV(models.Model):
     subscriber_id = models.CharField(max_length=7) 
     user_defined_id = models.CharField(max_length=20)
     chartcom = models.CharField(max_length=100, primary_key=True)
     dn = models.CharField(max_length=60)
     service_type = models.CharField(max_length=20)
     service_status = models.CharField(max_length=15)
     location_id = models.IntegerField(9, null=False)
     building = models.CharField(max_length=25)
     floor = models.CharField(max_length=18)
     room = models.CharField(max_length=18)
     jack = models.CharField(max_length=30)
     mrc_charged = models.CharField(max_length=1)
     toll_charged = models.CharField(max_length=1)
     local_charged = models.CharField(max_length=1)
 
     class Meta:
          managed = False
          ordering = ('chartcom',)
          db_table = 'PINN_CUSTOM\".\"um_osc_acct_subscribers_v'


# This view uses a copy of the Space Management building table
#  and only includes the official builfing codes from MPathways
class UmOSCCampusBuildingV(models.Model):
     campus_code = models.CharField(max_length=4,null=True)
     campus_desc = models.CharField(max_length=30,null=True)
     building_code = models.CharField(max_length=10,primary_key=True)
     building_name = models.CharField(max_length=25,null=True) 

     class Meta:
          managed = False
          ordering = ('campus_code','building_code')
          db_table = 'PINN_CUSTOM\".\"um_osc_campus_building_v'

     def __str__(self):
          return self.building_name


class UmOscInvReptLogV(models.Model):
     billing_date = models.DateField(null=True)
     timestamp = models.DateTimeField(null=True)

     class Meta:
          managed = False
          ordering = ('billing_date',)
          db_table = 'PINN_CUSTOM\".\"um_osc_inv_rept_log_v'


class UmOscBillCycleV(models.Model):
     billing_cycle = models.CharField(max_length=2)
     description = models.CharField(max_length=25)
     billing_month = models.CharField(max_length=3)
     billing_year = models.CharField(max_length=4)
     billing_date = models.DateField(null=True)
     batch_id = models.CharField(max_length=6)
     batch_date = models.DateField(null=True)
     start_date = models.DateField(null=True)
     end_date = models.DateField(null=True)
     row_id = models.CharField(max_length=20, primary_key=True)

     class Meta:
          managed = False
          ordering = ('billing_cycle','billing_date')
          db_table = 'PINN_CUSTOM\".\"um_osc_bill_cycle_v'


class UmOscDtDeptAcctListV(models.Model):
     fund = models.CharField(max_length=30)
     deptid = models.CharField(max_length=30, primary_key=True) #made this a primary key
     program = models.CharField(max_length=30)
     subclass = models.CharField(max_length=30)
     projectgrant = models.CharField(max_length=30) #changed name from project_grant
     account_number = models.CharField(max_length=100)
     batch_date = models.DateField

     class Meta:
          managed = False
          ordering = ('account_number',)
          db_table = 'PINN_CUSTOM\".\"um_osc_dt_dept_acct_list_v'


class UmOscAcctdetailMrcOccV(models.Model):
     subscriber_id = models.CharField(max_length=7)
     billing_date = models.DateField(null=True) # made this null=True
     billing_cycle = models.CharField(max_length=2)
     item_code = models.CharField(max_length=50)
     batch_date = models.DateField
     invoice_date = models.DateField(null=True) # made this null=True
     account_number = models.CharField(max_length=100)
     account_subcode = models.CharField(max_length=10)
     item_description = models.CharField(max_length=100)
     charge_type = models.CharField(max_length=3)
     charge_amount = models.DecimalField(decimal_places=4, max_digits=19,  null=False)
     spec_process_ind = models.CharField(max_length=1)
     package_code = models.CharField(max_length=91)
     quantity = models.IntegerField(9, null=False)
     unit_price = models.DecimalField(decimal_places=4, max_digits=19,  null=False)
     charge_to_dept = models.CharField(max_length=10)
     row_id = models.CharField(max_length=20, primary_key=True)
     user_defined_id =  models.CharField(max_length=20, blank=True)
     dtl_of_chrgs_telephony = models.PositiveIntegerField(null=True)            
     dtl_of_chrgs_nontelephony = models.PositiveIntegerField(null=True) 
     unique_identifier = models.CharField(max_length=200)
     charge_name = models.CharField(max_length=100)
     shortcode = models.CharField(max_length=6)
     quantity_vouchered = models.IntegerField(9)
     invoice_id = models.CharField(max_length=30)
     uniqname = models.CharField(max_length=8)
     voucher_comment = models.CharField(max_length=30)

     class Meta:
          managed = False
          ordering = ('account_number',)
          db_table = 'PINN_CUSTOM\".\"um_osc_acctdetail_mrc_occ_v'


class UmOscOtsCallSummaryV(models.Model):
     unique_key =  models.CharField(max_length=165, blank=True, null=True)        
     account_number =  models.CharField(max_length=100, blank=True, null=True)    
     fund =  models.CharField(max_length=30, blank=True, null=True)              
     deptid =  models.CharField(max_length=30, blank=True, null=True)            
     program =  models.CharField(max_length=30, blank=True, null=True)           
     class_code =  models.CharField(max_length=30, blank=True, null=True)             
     project_grant =  models.CharField(max_length=30, blank=True, null=True)     
     billing_date =  models.DateField(null=True)                                  
     user_defined_id =  models.CharField(max_length=20, blank=True, null=False, primary_key=True) #temporarily made this a primary key and set null to false    
     subscriber_id =  models.CharField(max_length=7, blank=True, null=True)      
     ld_count =  models.BigIntegerField( null=True)                               
     ld_amount =  models.BigIntegerField( null=True)                              
     lcl_count =  models.BigIntegerField( null=True)                              
     lcl_amount =  models.BigIntegerField( null=True)                             
     tot_call_count =  models.BigIntegerField( null=True)                         
     tot_call_amount =  models.BigIntegerField( null=True)                        
     mrc_count =  models.BigIntegerField( null=True)                              
     mrc_amount =  models.BigIntegerField( null=True)                             
     occ_count =  models.BigIntegerField( null=True)                              
     occ_amount =  models.BigIntegerField( null=True)                             
     fcc_count =  models.BigIntegerField( null=True)                              
     fcc_amount =  models.BigIntegerField( null=True)                             
     tot_count =  models.BigIntegerField( null=True)                              
     tot_amount =  models.BigIntegerField( null=True)                             
     row_id =  models.CharField(max_length=165, blank=True, null=True)
     dtl_of_chrgs_telephony = models.PositiveIntegerField(null=True)            
     dtl_of_chrgs_nontelephony = models.PositiveIntegerField(null=True)            

     class Meta:
          managed = False
          ordering = ('account_number',)
          db_table = 'PINN_CUSTOM\".\"um_osc_ots_call_summary_v'


class UmOscServiceLocV(models.Model):
     id =  models.BigIntegerField( null=False,primary_key=True)                                    
     billing_date =  models.DateField(null=True)                                  
     subscriber_id =  models.CharField(max_length=7, blank=True, null=True)       
     service_id =  models.BigIntegerField( null=False)                            
     location_id =  models.BigIntegerField( null=False)                           
     timestamp =  models.DateField(null=True)                                     
     department_number =  models.CharField(max_length=15, blank=True, null=True)  
     service_number =  models.CharField(max_length=60, blank=True, null=True)     
     status =  models.CharField(max_length=15, blank=True, null=True)             
     service_type =  models.CharField(max_length=20, blank=True, null=True)       
     building_id =  models.CharField(max_length=18, blank=True, null=True)        
     building =  models.CharField(max_length=25, blank=True, null=True)           
     floor =  models.CharField(max_length=18, blank=True, null=True)              
     floor_desc =  models.CharField(max_length=50, blank=True, null=True)         
     room =  models.CharField(max_length=18, blank=True, null=True)               
     room_desc =  models.CharField(max_length=50, blank=True, null=True)          
     jack =  models.CharField(max_length=30, blank=True, null=True)               
     service_class_id =  models.CharField(max_length=5, blank=True, null=True)    
     service_class_desc =  models.CharField(max_length=25, blank=True, null=True) 

     class Meta:
          managed = False
          ordering = ('billing_date',)
          db_table = 'PINN_CUSTOM\".\"um_osc_service_loc_v'

class UmOscRatedV(models.Model):
     row_id =  models.CharField(max_length=85, blank=True, null=False, primary_key=True) # made a primary key and set null to false            
     subscriber_id =  models.CharField(max_length=7, blank=True, null=True)      
     connect_date =  models.DateField(null=True)                                  
     billing_cycle =  models.CharField(max_length=2, blank=True, null=True)       
     batch_date =  models.DateField(null=True)                                    
     cos_code =  models.CharField(max_length=2, blank=True, null=True)            
     from_number =  models.CharField(max_length=20, blank=True, null=True)        
     pbn =  models.CharField(max_length=15, blank=True, null=True)                
     to_number =  models.CharField(max_length=20, blank=True, null=True)          
     call_duration =  models.BigIntegerField( null=True)                          
     dur_mn =  models.BigIntegerField( null=True)                                 
     dur_ss =  models.BigIntegerField( null=True)                                 
     call_type =  models.CharField(max_length=20, blank=True, null=True)          
     place_name =  models.CharField(max_length=25, blank=True, null=True)        
     state_name =  models.CharField(max_length=2, blank=True, null=True)          
     amount_billed =  models.BigIntegerField( null=True)                          
     posted_date =  models.DateField(null=True)                                   
     call_description =  models.CharField(max_length=64, blank=True, null=True)  
     expense_account =  models.CharField(max_length=100, blank=True, null=True)   

     class Meta:
          managed = False
          ordering = ('batch_date','billing_cycle')
          db_table = 'PINN_CUSTOM\".\"um_osc_rated_v'


class UmOscReptInvlocV(models.Model):
     id =  models.BigIntegerField( null=False,primary_key=True)                                     
     billing_date =  models.DateField(null=True)                                  
     subscriber_id =  models.CharField(max_length=7, blank=True, null=True)       
     user_defined_id =  models.CharField(max_length=20, blank=True, null=True)    
     user_defined_id_type =  models.CharField(max_length=80, blank=True, null=True)                                                                               
     cd_descr =  models.CharField(max_length=100, blank=True, null=True)          
     chartfield =  models.CharField(max_length=79, blank=True, null=True)         
     fund =  models.CharField(max_length=15, blank=True, null=True)               
     org =  models.CharField(max_length=15, blank=True, null=True)                
     program =  models.CharField(max_length=15, blank=True, null=True)            
     subclass =  models.CharField(max_length=15, blank=True, null=True)           
     project_grant =  models.CharField(max_length=15, blank=True, null=True)      
     l_use =  models.CharField(max_length=1, blank=True, null=True)               
     t_use =  models.CharField(max_length=1, blank=True, null=True)               
     m_use =  models.CharField(max_length=1, blank=True, null=True)               
     usage =  models.CharField(max_length=5, blank=True, null=True)              
     last_call_date =  models.DateField(null=True)                                
     first_name =  models.CharField(max_length=15, blank=True, null=True)         
     last_name =  models.CharField(max_length=20, blank=True, null=True)          
     title =  models.CharField(max_length=20, blank=True, null=True)              
     mrc_account =  models.CharField(max_length=10, blank=True, null=True)        
     item_code =  models.CharField(max_length=50, blank=True, null=True)         
     item_description =  models.CharField(max_length=100, blank=True, null=True)  
     quantity =  models.BigIntegerField( null=True)                               
     unit_price =  models.BigIntegerField( null=True)                             
     charge_amount =  models.BigIntegerField( null=True)                          
     remove_date =  models.DateField(null=True)                                   
     rectype =  models.CharField(max_length=1, blank=True, null=True)             
     location_since_date =  models.DateField(null=True)                           
     multiple_locations_flag =  models.CharField(max_length=1, blank=True, null=True)                                                                             
     building =  models.CharField(max_length=25, blank=True, null=True)           
     floor =  models.CharField(max_length=18, blank=True, null=True)              
     room =  models.CharField(max_length=18, blank=True, null=True)               
     jack =  models.CharField(max_length=30, blank=True, null=True)               
     ncos =  models.CharField(max_length=5, blank=True, null=True)                
     ncos_desc =  models.CharField(max_length=25, blank=True, null=True)          
     rptorder = models.CharField(max_length=1, blank=True, null=True)  
       
     class Meta:
          managed = False
          ordering = ('billing_date','org','chartfield','user_defined_id','rptorder','item_code')
          db_table = 'PINN_CUSTOM\".\"um_osc_rept_invloc_v'

class UmOscPhoneHistoryV(models.Model):
     date_snapshot = models.DateField(null=True)
     user_defined_id = models.CharField(max_length=20, primary_key=True) #made this a primary key
     phone_number = models.CharField(max_length=30)
     description = models.CharField(max_length=60)
       
     class Meta:
          managed = False
          ordering = ('user_defined_id','date_snapshot')
          db_table = 'PINN_CUSTOM\".\"um_osc_phone_history_v'

class UmOscRptSubscrib_Api_V(models.Model):
     um_osc_rpt_subscrib_id = models.PositiveIntegerField()
     subscriber_prefix = models.CharField(max_length=3, primary_key=True)
     subscriber_desc = models.CharField(max_length=100)
     active = models.PositiveIntegerField()
     chartfield_change = models.PositiveIntegerField()
     dtl_of_chrgs_telephony = models.PositiveIntegerField()
     dtl_of_chrgs_nontelephony = models.PositiveIntegerField()
     inv_loc_rept = models.PositiveIntegerField()
     create_date = models.DateField()
     created_by = models.CharField(max_length=50)
     last_update_date = models.DateField(null=True)
     last_updated_by = models.CharField(max_length=50, null=True)
     inactivation_date = models.DateField(null=True)
     inactivated_by = models.CharField(max_length=50, null=True)
       
     class Meta:
          managed = False
          ordering = ('subscriber_prefix',)
          db_table = 'PS_RATING\".\"um_osc_rpt_subscrib_api_v'

class UmRteCurrentTimeAssignedV(models.Model):
    wo_labor_id = models.IntegerField(primary_key=True)
    wo_tcom_id = models.FloatField()
    category_code = models.CharField(max_length=1)
    project_type_code = models.CharField(max_length=3, blank=True, null=True)
    project_number = models.FloatField(blank=True, null=True)
    project_name = models.CharField(max_length=50, blank=True, null=True)
    work_order_display = models.CharField(max_length=98, blank=True, null=True)
    pre_order_number = models.BigIntegerField(blank=True, null=True)
    pre_order_issue = models.BigIntegerField(blank=True, null=True)
    wo_type_code = models.CharField(max_length=2, blank=True, null=True)
    wo_number = models.IntegerField(blank=True, null=True)
    wo_issue = models.IntegerField(blank=True, null=True)
    status_name = models.CharField(max_length=60, blank=True, null=True)
    work_status_name = models.CharField(max_length=71, blank=True, null=True)
    assigned_labor_code = models.CharField(max_length=9, blank=True, null=True)
    is_occ_billed = models.FloatField(blank=True, null=True)
    billed = models.CharField(max_length=3, blank=True, null=True)
    labor_code = models.CharField(max_length=9, blank=True, null=True)
    labor_name_display = models.CharField(max_length=104, blank=True, null=True)
    skill_code = models.CharField(max_length=3, blank=True, null=True)
    skill_name = models.CharField(max_length=25, blank=True, null=True)
    rate_number = models.ForeignKey('UmRteRateLevelV', db_column='rate_number', to_field='labor_rate_level_code',
                                    on_delete=models.CASCADE)
    labor_cost_name = models.CharField(max_length=60, blank=True, null=True)
    rate_used = models.DecimalField(max_digits=19, decimal_places=4)
    assigned_date = models.DateField(blank=True, null=True)
    actual_mins = models.BigIntegerField()
    actual_mins_display = models.CharField(max_length=10, blank=True, null=True)
    assn_wo_group_code = models.CharField(max_length=32, blank=True, null=True)
    assn_wo_group_name = models.CharField(max_length=64, blank=True, null=True)
    comment_text = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_RTE_CURRENT_TIME_ASSIGNED_V'


class UmRteLaborGroupV(models.Model):
    wo_group_labor_id = models.BigIntegerField(primary_key=True)
    wo_group_labor_group_id = models.BigIntegerField()
    wo_group_code = models.CharField(max_length=32, blank=True, null=True)
    wo_group_name = models.CharField(max_length=64, blank=True, null=True)
    labor_id = models.IntegerField()
    wo_group_labor_code = models.CharField(max_length=9)
    labor_name_display = models.CharField(max_length=104, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_RTE_LABOR_GROUP_V'


class UmRteRateLevelV(models.Model):
    labor_rate_level_code = models.CharField(max_length=20, primary_key=True)
    labor_rate_level_name = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_RTE_RATE_LEVEL_V'


class UmRteServiceOrderV(models.Model):
    wo_tcom_id = models.FloatField(primary_key=True)
    full_prord_wo_number = models.CharField(max_length=98, blank=True, null=True)
    pre_order_number = models.BigIntegerField(blank=True, null=True)
    pre_order_issue = models.BigIntegerField(blank=True, null=True)
    wo_type_code = models.CharField(max_length=2, blank=True, null=True)
    wo_number = models.IntegerField(blank=True, null=True)
    wo_issue = models.IntegerField(blank=True, null=True)
    status_name = models.CharField(max_length=60, blank=True, null=True)
    category_code = models.CharField(max_length=1)
    assigned_labor_code = models.CharField(max_length=9, blank=True, null=True)
    comment_text = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_RTE_SERVICE_ORDER_V'


class UmRteTechnicianV(models.Model):
    labor_id = models.IntegerField(primary_key=True)
    labor_code = models.CharField(max_length=9)
    labor_name_display = models.CharField(max_length=4000, blank=True, null=True)
    labor_name_display2 = models.CharField(max_length=4000, blank=True, null=True)
    uniqname = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_RTE_TECHNICIAN_V'

class UmRteInput(models.Model):
  uniqname = models.CharField(max_length=8, blank=True, null=True)
  wo_labor_id = models.IntegerField()
  wo_tcom_id = models.FloatField()
  full_prord_wo_number = models.CharField(max_length=98, blank=True, null=True)
  labor_id = models.IntegerField()
  labor_code = models.CharField(max_length=9)
  wo_group_labor_group_id = models.BigIntegerField()
  wo_group_code = models.CharField(max_length=32, blank=True, null=True)
  assigned_date = models.DateField(blank=True, null=True)
  complete_date = models.DateTimeField(blank=True, null=True)
  rate_number = models.ForeignKey('UmRteRateLevelV', db_column='rate_number', to_field='labor_rate_level_code',
                                    on_delete=models.CASCADE)
  actual_mins_display = models.CharField(max_length=10, blank=True, null=True)
  notes = models.CharField(max_length=4000, blank=True, null=True)
  date_added = models.DateField(blank=True, null=True)
  date_processed = models.DateField(blank=True, null=True)
  messages = models.CharField(max_length=2000, blank=True, null=True)
  request_no = models.BigIntegerField(primary_key=True)

  class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_RTE_INPUT'

# Used for checking permissions on MBid and BOM
class UmBomProcurementUsersV(models.Model):
    username = models.CharField(max_length=100, null=False, primary_key=True)
    security_role_code = models.CharField(max_length=50, null=False)
    
    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_BOM_PROCUREMENT_USERS_V'

# MBid Tables

class UmEcommMbidCriticalDate(models.Model):
    bidding_year = models.CharField(max_length=4, primary_key=True)
    bidding_month = models.CharField(max_length=2)
    bidding_closed = models.CharField(max_length=1)

    bidding_open_time = models.DateTimeField()
    bidding_open_date = models.DateTimeField()
    bidding_close_time = models.DateTimeField()
    bidding_close_date = models.DateTimeField()

    date_created = models.DateTimeField()
    date_last_updated = models.DateTimeField()

    show_lowest_bid = models.CharField(max_length=3)
    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_ECOMM_MBID_CRITICAL_DATES'


# Write CSVs to here
class UmEcommMbidVendorInput(models.Model):
    bidding_year = models.CharField(max_length=4, null=True)
    bidding_month = models.CharField(max_length=2, null=True)
    bidding_closed = models.CharField(max_length=1, null=True)

    item_code = models.CharField(max_length=12, primary_key=True)
    item_desc = models.CharField(max_length=50, null=True)
    subclass_id = models.CharField(max_length=4, null=True)
    manufacturer_name = models.CharField(max_length=50, null=True)
    manufacturer_part_number=models.CharField(max_length=50, null=True)
    vendor_price = models.FloatField()
    vendor_notes = models.CharField(max_length=2000, null=True)

    vendor_id = models.CharField(max_length=11, null=True)
    vendor_name = models.CharField(max_length=50, null=True)
    vendor_address1 = models.CharField(max_length=35, null=True)
    vendor_address2 = models.CharField(max_length=35, null=True)
    vendor_city = models.CharField(max_length=25, null=True)
    vendor_state = models.CharField(max_length=2, null=True)
    vendor_zip_code = models.CharField(max_length=2, null=True)
    vendor_zip_ext = models.CharField(max_length=2, null=True)
    vendor_itemno = models.CharField(max_length=50, null=True) #dont know where this comes from
    
    vendor_rank = models.IntegerField()

    vendor_chosen = models.CharField(max_length=1, null=True)
    date_created = models.DateTimeField()
    date_last_updated = models.DateTimeField()
    vendor_email_address = models.CharField(max_length=50, null=True)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_ECOMM_MBID_VENDOR_INPUT'


class UmEcommMbidWarehseInput(models.Model):
    bidding_year = models.CharField(max_length=4)
    bidding_month = models.CharField(max_length=2)
    bidding_closed = models.CharField(max_length=1)

    item_code = models.CharField(max_length=12, primary_key=True)
    bid_status = models.CharField(max_length=30, null=True)
    um_notes = models.CharField(max_length=2000)
    annual_qty = models.IntegerField()
    qty_required = models.IntegerField()

    item_desc = models.CharField(max_length=50, null=True)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_ECOMM_MBID_WAREHSE_INPUT'


class UmEcommMbidCommodityV(models.Model):
    bidding_year = models.CharField(max_length=4)
    bidding_month = models.CharField(max_length=2)
    bidding_closed = models.CharField(max_length=1)
    
    item_code = models.CharField(max_length=12, primary_key=True)
    bid_status = models.CharField(max_length=30, null=True)
    um_notes = models.CharField(max_length=2000)
    annual_qty = models.IntegerField()
    qty_required = models.IntegerField()

    title = models.CharField(max_length=200)  # description

    subclass_id = models.CharField(max_length=16)
    manufacturer_id = models.CharField(max_length=512)  # SUTTLE
    uom = models.CharField(max_length=42)  # unit of measure  
    manufacturer_part_number = models.CharField(max_length=512) 

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_ECOMM_MBID_COMMODITY_V'


class UmEcommMbidVendorV(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64, null=True)
    contact_name = models.CharField(max_length=100)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    phone = models.CharField(max_length=50)
    fax = models.CharField(max_length=50)
    email_address = models.CharField(max_length=320)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_ECOMM_MBID_VENDOR_V'


class UmMpathDwCurrDepartment(models.Model):
    deptid = models.CharField(max_length=10)
    dept_effdt = models.DateField()
    dept_eff_status = models.CharField(max_length=1)
    dept_descr = models.CharField(max_length=30)
    emplid = models.CharField(max_length=11)
    dept_grp = models.CharField(max_length=20)
    dept_grp_descr = models.CharField(max_length=30)
    dept_grp_vp_area = models.CharField(max_length=20)
    dept_grp_vp_area_descr = models.CharField(max_length=30)
    dept_grp_campus = models.CharField(max_length=20)
    dept_grp_campus_descr = models.CharField(max_length=30)
    dept_bud_seq = models.CharField(max_length=20, blank=True, null=True)
    dept_bud_seq_descr = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PINN_CUSTOM\".\"UM_MPATHDW_CURR_DEPARTMENT'