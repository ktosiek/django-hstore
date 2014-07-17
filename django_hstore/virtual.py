from django.db import models


def _add_hstore_virtual_fields_to_fields(self):
    """
    add hstore virtual fields to model meta fields
    """
    for field in self._meta.hstore_virtual_fields:
        if field not in self._meta.fields:
            self._meta.fields.append(field)

def _remove_hstore_virtual_fields_from_fields(self):
    """
    remove hstore virtual fields from model meta fields
    """
    for field in self._meta.hstore_virtual_fields:
        self._meta.fields.remove(field)


class HStoreVirtualMixin(object):
    """
    must be mixed-in with django fields
    """
    def contribute_to_class(self, cls, name, virtual_only=True):
        super(HStoreVirtualMixin, self).contribute_to_class(cls, name, virtual_only)
        
        # add hstore_virtual_fields attribute to class
        if not hasattr(cls._meta, 'hstore_virtual_fields'):
            cls._meta.hstore_virtual_fields = []
        # add this field to hstore_virtual_fields
        cls._meta.hstore_virtual_fields.append(self)
        
        if not hasattr(cls, '_add_hstore_virtual_fields_to_fields'):
            cls._add_hstore_virtual_fields_to_fields = _add_hstore_virtual_fields_to_fields
        
        if not hasattr(cls, '_remove_hstore_virtual_fields_from_fields'):
            cls._remove_hstore_virtual_fields_from_fields = _remove_hstore_virtual_fields_from_fields
        
        # Connect myself as the descriptor for this field
        setattr(cls, name, self)
    
    # begin descriptor methods
    
    def __get__(self, instance, instance_type=None):
        """
        retrieve value from hstore dictionary
        """
        if instance is None:
            raise AttributeError('Can only be accessed via instance')
        
        return getattr(instance, self.hstore_field_name).get(self.name, self.default)
    
    def __set__(self, instance, value):
        """
        set value on hstore dictionary
        """
        hstore_dictionary = getattr(instance, self.hstore_field_name)
        hstore_dictionary[self.name] = value
    
    # end descriptor methods


def create_hstore_virtual_field(field, kwargs={}):
    """
    returns an instance of an HStore virtual field which is mixed with the specified field class
    and initializated with the kwargs passed
    """
    if isinstance(field, basestring):
        BaseField = getattr(models, field)
    elif isinstance(field, models.Field):
        BaseField = field
    else:
        raise ValueError('field must be either a django standard field or a subclass of django.db.models.Field')
        
    class VirtualField(HStoreVirtualMixin, BaseField):
        def __init__(self, *args, **kwargs):
            try:
                self.hstore_field_name = kwargs.pop('hstore_field_name')
            except KeyError:
                raise ValueError('missing hstore_field_name keyword argument')
            super(VirtualField, self).__init__(*args, **kwargs)
    
    return VirtualField(**kwargs)


__all__ = ['create_hstore_virtual_field']