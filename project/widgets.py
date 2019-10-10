from django import forms

class Select2Mixin():
    class Media:
        css = {
            'all': ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/css/select2.min.css",)
        }
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.6-rc.0/js/select2.min.js",
              '/project/static/js/customselect2.js')

    def update_attrs(self, options, attrs):
        attrs = self.fix_class(attrs)
        multiple = options.pop('multiple', False)
        attrs['data-adapt-container-css-class'] = 'true'

        if multiple:
            attrs['multiple'] = 'true'

        for key, val in options.items():
            attrs['data-{}'.format(key)] = val

        return attrs

    def fix_class(self, attrs):
        class_name = attrs.pop('class', '')
        if class_name:
            attrs['class'] = '{} {}'.format(
                class_name, 'custom-select2-widget')
        else:
            attrs['class'] = 'custom-select2-widget'

        return attrs


class Select2Widget(Select2Mixin, forms.widgets.Select):
    def __init__(self, attrs=None, choices=(), *args, **kwargs):

        attrs = attrs or {}
        options = kwargs.pop('options', {})
        new_attrs = self.update_attrs(options, attrs)

        super().__init__(new_attrs)
        self.choices = list(choices)