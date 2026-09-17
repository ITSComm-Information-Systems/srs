from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
import datetime

from project.integrations import Slack
from project.utils import get_query_result


class Command(BaseCommand):
    help = 'Compare billing totals to Pinnacle and prior months.'

    def handle(self, *args, **options):
        
        sql = '''
                WITH 
                service AS
                    (SELECT distinct
                        data_source,
                        service_type_code,
                        subscriber_prefix
                    FROM ps_rating.UM_BILL_VALID_SVCS_API_V
                    WHERE subscriber_prefix IN
                        ('SV', 'ST', 'TU', 'LK', 'CS', 'MB', 'VC', 'DD', 'MD' )
                    ORDER by data_source),
                curr AS
                    (SELECT DATA_SOURCE , count(*) AS units, sum(TOTAL_AMOUNT) AS amount
                    FROM ps_rating.um_bill_input_api_v 
                    WHERE date_processed >= TRUNC(SYSDATE, 'MM')
                    GROUP BY data_source),
                prev AS
                    (SELECT DATA_SOURCE , count(*) AS units, sum(TOTAL_AMOUNT ) AS amount
                    FROM ps_rating.um_bill_input_api_v 
                    WHERE date_processed >= ADD_MONTHS(TRUNC(SYSDATE, 'MM'), -1)
                    AND date_processed <  TRUNC(SYSDATE, 'MM')	
                    GROUP BY data_source),
                pinn as (select service_type, count(*) as units , sum(one_time_total) as amount
                                from TELECOM.ONE_TIME_CHARGE_API_V
                                where installments_remaining = 1      
                                group by service_type)
                SELECT service.data_source, curr.units, curr.amount, 
                curr.units - pinn.units AS pinn_units, 
                curr.amount - pinn.amount AS pinn_amount,
                curr.units - prev.units AS prev_units,
                curr.amount - prev.amount AS prev_amount
                FROM service
                LEFT JOIN curr ON curr.data_source = service.DATA_SOURCE 
                LEFT JOIN prev ON prev.data_source = service.DATA_SOURCE 
                LEFT JOIN pinn ON pinn.service_type = service.service_type_code 
            '''

        instances = get_query_result(sql)
        message = render_to_string('project/billing_audit.html', {'instances': instances})

        Slack(message, channel='inf-billing')





