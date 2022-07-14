import csv
from django.http import HttpResponse 

def download_csv_from_queryset(queryset):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="full_list.csv"'

    writer = csv.writer(response)
    fields = queryset.model._meta.fields

    choice_related = []
    row = []
    for field in fields:
        row.append(field.name)
        if field.related_model:
            choice_related.append(field.name)

    writer.writerow(row)

    #instance_list = list(self.model.objects.all().select_related(*choice_related))
    for instance in queryset:
        row = []
        for field in fields:
                row.append(getattr(instance,field.name))

        writer.writerow(row)

    return response