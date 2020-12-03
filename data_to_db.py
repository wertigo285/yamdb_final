import csv
import sys
import os
from dataclasses import dataclass

import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'api_yamdb.settings'
django.setup()

from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User

@dataclass
class File:
    path: str
    model: object
    name: str
    field: str = None


def import_data_from_csv(data_file):
    with open(data_file.path, encoding='utf-8') as f:
        data = csv.DictReader(f)
        if data_file.field is None:
            for row in data:
                instance = data_file.model()
                for item in row.items():
                    name = item[0]
                    value = item[1]
                    field = data_file.model._meta.get_field(name)
                    if field.remote_field and not name.endswith('id'):
                        value = field.remote_field.model.objects.get(id=value)
                    setattr(instance, name, value)
                instance.save()
        else:
            many_to_many = {}
            id_fname = f'{data_file.name.lower()}_id'
            fk_fname = f'{data_file.field.lower()}_id'
            for row in data:
                key = row[id_fname]
                if not key in many_to_many.keys():
                    many_to_many[key] = []
                many_to_many[key].append(row[fk_fname])
            for k, v in many_to_many.items():
                instance = data_file.model.objects.get(pk=k)
                field = data_file.model._meta.get_field(data_file.field)
                if field.remote_field:
                    value = field.remote_field.model.objects.filter(id__in=v)
                attr = getattr(instance, data_file.field, value)
                for v in value:
                    attr.add(v)
                instance.save()


if __name__ == '__main__':
    classes = globals().keys()
    path_start = f'{sys.path[0]}\\data\\'
    files = {}
    for f in os.scandir(path_start):
        if f.name.endswith('.csv'):
            class_name = f.name.replace('.csv', '').capitalize()
            if class_name in classes:
                name = class_name
                model = globals()[class_name]
                field = None
            else:
                many_to_many = class_name.split('_')
                name = many_to_many[1]
                model = globals()[name.capitalize()]
                field = many_to_many[0].lower()
            
            files[class_name] = File(path=f.path, model=model, name=name, field=field)


    import_data_from_csv(files['Category'])
    import_data_from_csv(files['Genre'])
    import_data_from_csv(files['User'])
    import_data_from_csv(files['Title'])
    import_data_from_csv(files['Review'])
    import_data_from_csv(files['Comment'])
    import_data_from_csv(files['Genre_title'])
