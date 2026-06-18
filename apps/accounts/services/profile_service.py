import hashlib


def get_user_initials(user):
    name = (user.first_name or user.email or user.username or '?')
    return name[0].upper()


def get_user_color(user):
    colors = ['#7c3aed', '#6d4aff', '#2ecc71', '#f59e0b', '#e84040', '#3b82f6', '#ec4899']
    idx = hash(str(user.id)) % len(colors)
    return colors[idx]
