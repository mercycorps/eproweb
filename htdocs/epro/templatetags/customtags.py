from django import template
from eproweb import utils


register = template.Library()

@register.filter
def running_total(fine_list):
    """
    Usage:
        In your template call the customtags file like this
        {% load customtags %}
        i guess by this time you have a list of dict that you passed from your
        view lets say its called "fines"

        {% for fine in fines %}
            Display your fine items inside this loop
        {% endfor %}

        outside the loop call the customtag like this
        <b> {{ fines.list|running_total }} </b>
    """
    return sum(d.get('fine_sum') for d in fine_list)


@register.filter(name='humanize_bytes')
def humanize_bytes(value, precision=1):
    """
    Generate a humanized version of a file size.
    :param value:
    :param precision:
    :return:
    """
    abbrevs = (
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'bytes')
    )
    if value == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if value >= factor:
            break
    return '%.*f %s' % (precision, value / factor, suffix)


@register.filter(is_safe=True)
def describe_seconds(value):
    """
    Convert a seconds value into a human readable (ie week, day, hour) value.
    :param value: integer value of the number of seconds.
    :return: a string with the humanized value.
    """
    return utils.describe_seconds(value)


@register.filter(name='get_due_date_string')
def get_due_date_string(value):
    """
    {{ todo.due_date|get_due_date_string }}
    """
    delta = value - date.today()

    if delta.days == 0:
        return "Today!"
    elif delta.days < 1:
        return "%s %s ago!" % (abs(delta.days),
            ("day" if abs(delta.days) == 1 else "days"))
    elif delta.days == 1:
        return "Tomorrow"
    elif delta.days > 1:
        return "In %s days" % delta.days


@register.filter(name='get_due_date_color')
def get_due_date_color(value):
    """
    div style='border: 2px solid {{todo.due_date|get_due_date_color}};'>
    """
    delta = value - date.today()

    if delta.days < 1:
        return "#FF0000"
    elif delta.days <= 3 :
        return "#FF7400"
    else:
        return "#00CC00"

@register.filter(is_safe=True)
def url_target_blank(text):
    return text.replace('<a ', '<a target="_blank" ')


@register.filter
def can_edit(user, obj):
    """
    For checking edit permission on an object in templates;
    usage:
        {% if user|can_edit:my_obj %}
            <a href="{% url 'my_obj:edit' my_obj.id %}">
                Edit Object
            </a>
        {% endif %}

    More applications of something like this:
        {% if user|can_delete:my_obj %}
        {% if user|is_in_group:group %}
        {% if event|is_attended_by:user %}
        {% if user|has_been_at:place %}
        {% if place|is_in_favorites_of:user %}
        {% if article|has_been_flagged_by:user %}
    """
    user_can_edit = False

    if user.is_authenticated:
        if user.is_superuser:
            user_can_edit = True
        else:
            if obj and obj.user and obj.user == user:
                user_can_edit = True
    return user_can_edit
