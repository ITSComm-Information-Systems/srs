from django.db import models

class SrsRteVsEstimate(models.Model):
    wo_tcom_id = models.FloatField(primary_key=True)
    project_name = models.CharField(max_length=50, blank=True, null=True)
    skill_code = models.CharField(max_length=3, blank=True, null=True)
    assn_wo_group_code = models.CharField(max_length=32, blank=True, null=True)
    assigned_labor_code = models.CharField(max_length=9, blank=True, null=True)
    labor_code = models.CharField(max_length=9, blank=True, null=True)
    reported_hours = models.FloatField(blank=True, null=True)
    est_hours = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'PINN_CUSTOM\".\"srs_rte_vs_estimate'

    def __str__(self):
        return f"{self.wo_tcom_id}"