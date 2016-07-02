from app.models import Place


def get_all():
    return Place.objects.all()


def create(name, address):
    return Place.objects.create(name=name, address=address)