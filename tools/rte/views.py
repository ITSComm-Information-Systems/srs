from django.http import HttpResponse
from django.template import loader

# Base RTE view
def load_rte(request):
    template = loader.get_template('rte/base_rte.html')

    context = {
        'title': 'Rapid Time Entry'
    }
    return HttpResponse(template.render(context, request))