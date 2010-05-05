from django.db.models.query import CollectedObjects
from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ForeignKey
from django.forms.models import model_to_dict


def _has_field(model_cls, fieldname):
    """True if model_cls has fieldname."""
    try:
        return model_cls._meta.get_field_by_name(fieldname) and True
    except:
        return False

def update_related_fields(obj, update):
    """
    Update all attributes in dict update for all objects related to obj.
    Based on the delete object code: http://bit.ly/osrZf
    """
    collected_objs = CollectedObjects()
    obj._collect_sub_objects(collected_objs)
    models = collected_objs.keys()
    for model in models:
        instance_tuple = collected_objs[model].items()
        pk_list = [pk for pk, instance in instance_tuple]
        # Update fields in the model.
        updates = update.copy()
        [updates.pop(fn) for fn in updates.keys() if not _has_field(model, fn)]
        model._default_manager.filter(id__in=pk_list).update(**updates)

def duplicate(obj, update=None, model_order=None):
    """
    Duplicate all related objects of obj updating attributes using dict update.
    If a duplicated objects has a FK to another duplicated object then update 
    that. Returns the duplicate copy of obj.
        
    model_order is a list of models which specify in which order objects should
    be saved.

    This function offers acceptable performance on small object trees.
    """
    #TODO: The reference to obj is lost - can we save it somehow?
    #TODO: What about m2m relationships?
    
    # We lose the reference to obj so store this so we can look it up again.
    obj_pk = getattr(obj, obj._meta.pk.name)
    
    collected_objs = CollectedObjects()
    obj._collect_sub_objects(collected_objs)
    related_models = collected_objs.keys()
    root_obj = None
    
    # Sometimes it's good enough just to save in reverse deletion order.
    if model_order is None:
        model_order = reversed(related_models)
        
    for model in model_order:
        if model not in collected_objs:
            continue

        # Find all FKs on model that point to a related_model.
        fks = []
        for f in model._meta.fields:        
            if isinstance(f, ForeignKey) and f.rel.to in related_models:
                fks.append(f)                

        # Replace each `sub_obj` with a duplicate.
        sub_objs = collected_objs[model]
        for pk_val, sub_obj in sub_objs.iteritems():
            for fk in fks:
                fk_value = getattr(sub_obj, "%s_id" % fk.name)
                # If this FK has been duplicated then point to the duplicate.
                if fk_value in collected_objs[fk.rel.to]:
                    dupe_obj = collected_objs[fk.rel.to][fk_value]
                    setattr(sub_obj, fk.name, dupe_obj)
            
            # Duplicate the object and save it.
            sub_obj.id = None
            for k, v in update.items():
                setattr(sub_obj, k, v)
            sub_obj.save()
            if root_obj is None:
                root_obj = sub_obj

    # Restore the reference to obj.
    obj = obj._default_manager.get(pk=obj_pk)

    return root_obj