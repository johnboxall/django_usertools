from django.db.models.query import CollectedObjects
from django.db.models.fields.related import ForeignKey
from django.forms.models import model_to_dict

def update_related_field(obj, value, field):
    """
    Set `field` to `value` for all objects related to `obj`.
    Based on heavily off the delete object code:
    http://code.djangoproject.com/browser/django/trunk/django/db/models/query.py#L824
    
    """
    # Collect all related objects.
    collected_objs = CollectedObjects()
    obj._collect_sub_objects(collected_objs)
    classes = collected_objs.keys()
    # Bulk update the objects for performance
    for cls in classes:
        items = collected_objs[cls].items()
        pk_list = [pk for pk, instance in items]
        cls._default_manager.filter(id__in=pk_list).update(**{field:value})
    return obj

def duplicate(obj, value, field, duplicate_order=None):
    """
    Duplicate all related objects of `obj` setting
    `field` to `value`. If one of the duplicate
    objects has an FK to another duplicate object
    update that as well. Return the duplicate copy
    of `obj`.
    
    duplicate_order is a list of models which specify how
    the duplicate objects are saved. For complex objects
    this can matter. Check to save if objects are being
    saved correctly and if not just pass in related objects
    in the order that they should be saved.
    
    """
    collected_objs = CollectedObjects()
    obj._collect_sub_objects(collected_objs)
    related_models = collected_objs.keys()
    root_obj = None
    
    # Sometimes it's good enough just to save in reverse deletion order.
    if duplicate_order is None:
        duplicate_order = reversed(related_models)
        
    for model in duplicate_order:
        # Find all FKs on model that point to a related_model.
        fks = []
        for f in model._meta.fields:
            if isinstance(f, ForeignKey) and f.rel.to in related_models:
                fks.append(f)                
        # Replace each `sub_obj` with a duplicate.
        sub_obj = collected_objs[model]
        for pk_val, obj in sub_obj.iteritems():        
            for fk in fks:
                fk_value = getattr(obj, "%s_id" % fk.name)
                # If this FK has been duplicated then point to the duplicate.
                if fk_value in collected_objs[fk.rel.to]:
                    dupe_obj = collected_objs[fk.rel.to][fk_value]
                    setattr(obj, fk.name, dupe_obj)
            # Duplicate the object and save it.
            obj.id = None
            setattr(obj, field, value)
            obj.save()
            if root_obj is None:
                root_obj = obj
    return root_obj