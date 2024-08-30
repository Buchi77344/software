from django.forms.widgets import FileInput

class MultiFileInput(FileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
        if attrs is None:
            attrs = {}
        attrs.update({'multiple': 'multiple'})

    def value_from_datadict(self, data, files, name):
        if files.getlist(name):
            return files.getlist(name)
        return None
