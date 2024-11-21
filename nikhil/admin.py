from django.contrib import admin
from .models import Hotels,Rooms,Reservation, Contact, Payment
# Register your models here.
admin.site.register(Hotels)
admin.site.register(Rooms)
admin.site.register(Reservation)
admin.site.register(Contact)
admin.site.register(Payment)