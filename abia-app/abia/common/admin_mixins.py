from abia.common.forms import LGAChoiceField


class LGAAdminMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name and 'lga' in db_field.name.lower():
            return LGAChoiceField()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
