from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
import datetime

from project.integrations import Slack
from project.utils import get_query_result


class Command(BaseCommand):
    help = 'Compare billing totals to Pinnacle and prior months.'

    def handle(self, *args, **options):
        
        sql = '''
                with curr as (select count(*) as recs, sum(total_amount) as cost, data_source
                from ps_rating.um_bill_input_api_v
                where bill_input_file_id = %s
                group by data_source ),

                prev as (select count(*) as recs, sum(total_amount) as cost, data_source
                from ps_rating.um_bill_input_api_v
                where bill_input_file_id =  %s
                group by data_source ),

                pinn as (select decode(service_type, 'Version Ctl Hosting','GitHub',service_type) as service_type, count(*) as recs , sum(one_time_total) as cost
                from TELECOM.ONE_TIME_CHARGE_API_V
                where installments_remaining = 1      
                group by service_type)

                select curr.*, curr.recs - prev.recs as prev_recs, curr.cost - prev.cost as prev_cost
                , curr.cost - pinn.cost as pinn_cost
                , curr.recs - pinn.recs as pinn_recs
                from curr
                left join prev on curr.data_source = prev.data_source
                left join pinn on curr.data_source = pinn.service_type
            '''

        today = datetime.date.today()
        curr = today.strftime("%-m15%Y")
        last_month = today.replace(day=1) - datetime.timedelta(days=1)
        prev = last_month.strftime("%-m15%Y")

        instances = get_query_result(sql, (curr, prev))

        message = render_to_string('project/billing_audit.html', {'instances': instances})

        Slack().send_message(message, 'inf-information_systems_no-interns')





