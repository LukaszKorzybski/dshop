from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec


class MainCategoryFilterSpec(RelatedFilterSpec):
    def __init__(self, f, request, params, model, model_admin):
        super(MainCategoryFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_choices = f.rel.to._default_manager.main_categories().values_list('id', 'name')

    def title(self):
        return u'kategoria'

FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'main_category_filter', False),
                                   MainCategoryFilterSpec))