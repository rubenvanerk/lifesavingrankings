from django import template
register = template.Library()


@register.inclusion_tag('tags/form.html')
def styled_fields(form):
    return {'form': form}
