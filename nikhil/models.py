from django.db import models
from django.contrib.auth.models import User

class Hotels(models.Model):
    name = models.CharField(max_length=30)
    owner = models.CharField(max_length=20)
    location = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    description = models.CharField(max_length=500000, default="")
    image_1 = models.ImageField(upload_to='hotels/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='hotels/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='hotels/', null=True, blank=True)

    def __str__(self):
        return self.name


class Rooms(models.Model):
    ROOM_STATUS = ( 
    ("1", "available"), 
    ("2", "not available"),    
    ) 

    ROOM_TYPE = ( 
    ("1", "Hotel"), 
    ("2", "Farm House"),
    ) 

    room_type = models.CharField(max_length=50,choices = ROOM_TYPE)
    capacity = models.IntegerField()
    price = models.IntegerField()
    size = models.IntegerField()
    hotel = models.ForeignKey(Hotels, on_delete = models.CASCADE)
    status = models.CharField(choices =ROOM_STATUS,max_length = 15)
    roomnumber = models.IntegerField()
    def __str__(self):
        return self.hotel.name

class Reservation(models.Model):

    check_in = models.DateField(auto_now =False)
    check_out = models.DateField()
    room = models.ForeignKey(Rooms, on_delete = models.CASCADE)
    guest = models.ForeignKey(User, on_delete= models.CASCADE)
    
    booking_id = models.CharField(max_length=100,default="null")
    def __str__(self):
        return self.guest.username


class Contact(models.Model):
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    message = models.CharField(max_length=50)


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=20)
    expiry_date = models.CharField(max_length=5)
    card_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment by {self.user.username} on {self.created_at}"