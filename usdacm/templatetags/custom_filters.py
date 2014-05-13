from django import template

register = template.Library()


"""
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
"""
@register.filter
def get_range( value ):
  return range( value )


@register.filter    
def subtract(value, arg):
    return value - arg


@register.filter
def get_class(obj):
  return obj.__class__.__name__



@register.filter
def widget_type(widget):
  type =  widget.__class__.__name__
  if type == 'TextInput':
    return 'text'
  elif type == 'FIleInput' or type == 'ClearableFileInput':
    return 'file'
  elif type == 'CheckboxInput':
    return 'checkbox'
  elif type == 'PasswordInput':
    return 'password'
  else:
    return 'text'

