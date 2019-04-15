# \osc\project\pinnmodels.py
# This is a hand-generated Django model module.
#   * 
#   * Made sure each model has one field with primary_key=True
#   * Made sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Kept `managed = False` lines if you wish to not  allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models



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
   wo_type_category_id =  models.NullBooleanField()
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
   approval_required =  models.NullBooleanField()
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
   new_subscriber =  models.NullBooleanField()
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
   new_service =  models.NullBooleanField()
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
   new_location =  models.NullBooleanField()
   created_loc_id =  models.BigIntegerField( null=True)
   created_path_id =  models.BigIntegerField( null=True)
   nena_create_date =  models.DateField(null=True)
   signoff_status_id =  models.IntegerField(9, null=True)
   signoff_status_name =  models.CharField(max_length=240, blank=True, null=True)
   signoff_required =  models.NullBooleanField()
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
   sla_escalation_on_hold =  models.NullBooleanField()
   sla_escalation_restart =  models.DateField(null=True)
   sla_respond_missed_dt =  models.NullBooleanField()
   sla_resolve_missed_dt =  models.NullBooleanField()
   wo_step_id =  models.IntegerField(9, null=True)
   wo_step_code =  models.CharField(max_length=200, blank=True, null=True)
   wo_step_name =  models.CharField(max_length=400, blank=True, null=True)
   quick_incident =  models.NullBooleanField()
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
   add_info_checkbox_1 =  models.NullBooleanField(verbose_name="Draft Comp-D")
   add_info_checkbox_2 =  models.NullBooleanField(verbose_name="Asbuilt Recv'd-D")
   add_info_checkbox_3 =  models.NullBooleanField(verbose_name="Asbuilt Compl-D")
   add_info_checkbox_4 =  models.NullBooleanField()
   add_info_checkbox_5 =  models.NullBooleanField(verbose_name="Asbuilt/Prints-F")
   add_info_checkbox_6 =  models.NullBooleanField(verbose_name="Closeout Compl-F")
   add_info_checkbox_7 =  models.NullBooleanField(verbose_name="Asbuilt/Prints Received-A")
   add_info_checkbox_8 =  models.NullBooleanField(verbose_name="Assignments Complete-A")
   add_info_checkbox_9 =  models.NullBooleanField()
   add_info_checkbox_10 =  models.NullBooleanField()
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
   move_svc_chars =  models.NullBooleanField()
   move_feat_items =  models.NullBooleanField()
   move_inventory =  models.NullBooleanField()
   subscriber_only_swap =  models.NullBooleanField()
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
