from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """Adds the argument to the value"""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(lst, index):
    """Gets an item from a list by index"""
    try:
        return lst[int(index)]
    except (IndexError, ValueError, TypeError):
        return None

@register.filter
def get_sub_board_winner(winners, index):
    """Gets the winner of a specific sub-board"""
    try:
        return winners[int(index)]
    except (IndexError, ValueError, TypeError):
        return None