import csv
from django.http import HttpResponse 

def download_csv_from_queryset(queryset, file_name='full_list'):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'

    writer = csv.writer(response)

    choice_related = []
    row = []

    if type(queryset[0]) == dict:
        fields = queryset[0].keys()
        for field in queryset[0].keys():
            row.append(field)

        writer.writerow(row)
        for rec in queryset:
            row = []
            for value in rec.values():
                row.append(value)
            writer.writerow(row)

        return response

    fields = queryset.model._meta.fields

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