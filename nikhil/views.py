from django.shortcuts import render ,redirect
from django.http import HttpResponse , HttpResponseRedirect
from .models import Hotels,Rooms,Reservation, Contact, Payment
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
import logging

# Create your views here.

#homepage
def homepage(request):
    return render(request, 'homepage.html')  # Rendering the homepage template

#book now
def booknow(request):
    # Retrieve all (location, id) pairs and remove duplicates based on location
    all_locations_with_ids = Hotels.objects.values_list('location', 'id').order_by('location')
    unique_locations = {}
    for location, hotel_id in all_locations_with_ids:
        if location not in unique_locations:
            unique_locations[location] = hotel_id

    # Convert dictionary to list of tuples
    all_location = list(unique_locations.items())

    if request.method == "POST":
        try:
            print(request.POST)
            hotel = Hotels.objects.get(id=int(request.POST['search_location']))
            rr = []

            # Find reserved rooms within the specified time period to exclude them from the query set
            for each_reservation in Reservation.objects.all():
                if (str(each_reservation.check_in) < str(request.POST['cin']) and
                        str(each_reservation.check_out) < str(request.POST['cout'])):
                    pass
                elif (str(each_reservation.check_in) > str(request.POST['cin']) and
                        str(each_reservation.check_out) > str(request.POST['cout'])):
                    pass
                else:
                    rr.append(each_reservation.room.id)

            room = Rooms.objects.filter(
                # hotel=hotel,
                capacity__gte=int(request.POST['capacity'])
            ).exclude(id__in=rr)
            
            if not room:
                messages.warning(request, "Sorry No Rooms Are Available on this time period")
                
            data = {'rooms': room, 'all_location': all_location, 'flag': True}
            response = render(request, 'index.html', data)
            
        except Exception as e:
            messages.error(request, e)
            response = render(request, 'index.html', {'all_location': all_location})

    else:
        data = {'all_location': all_location}
        response = render(request, 'index.html', data)

    return HttpResponse(response)


#about
def aboutpage(request):
    return HttpResponse(render(request,'about.html'))

#contact
def contactpage(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        location = request.POST.get('location')
        message = request.POST.get('message')

        # Create a new Contact object
        new_contact = Contact(
            name=name,
            email=email,
            location=location,
            message=message
        )
        new_contact.save()  # Save the contact to the database
        messages.success(request, "Thanks for contacting us. We will get back to you soon.")

        return redirect('contactpage')  # Redirect after submission to prevent resubmission

    return render(request, 'contact.html')

#user sign up
def user_sign_up(request):
    if request.method =="POST":
        user_name = request.POST['username']
        
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.warning(request,"Password didn't matched")
            return redirect('userloginpage')
        
        try:
            if User.objects.all().get(username=user_name):
                messages.warning(request,"Username Not Available")
                return redirect('userloginpage')
        except:
            pass
            

        new_user = User.objects.create_user(username=user_name,password=password1)
        new_user.is_superuser=False
        new_user.is_staff=False
        new_user.save()
        messages.success(request,"Registration Successfull")
        return redirect("userloginpage")
    return HttpResponse('Access Denied')

#staff sign up
def staff_sign_up(request):
    if request.method =="POST":
        user_name = request.POST['username']
        
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.success(request,"Password didn't Matched")
            return redirect('staffloginpage')
        try:
            if User.objects.all().get(username=user_name):
                messages.warning(request,"Username Already Exist")
                return redirect("staffloginpage")
        except:
            pass
        
        new_user = User.objects.create_user(username=user_name,password=password1)
        new_user.is_superuser=False
        new_user.is_staff=True
        new_user.save()
        messages.success(request," Staff Registration Successfull")
        return redirect("staffloginpage")
    else:

        return HttpResponse('Access Denied')
    
#user login and signup page
def user_log_sign_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['pswd']

        user = authenticate(username=email,password=password)
        try:
            if user.is_staff:
                
                messages.error(request,"Incorrect username or Password")
                return redirect('staffloginpage')
        except:
            pass
        
        if user is not None:
            login(request,user)
            messages.success(request,"Logged in Successfully")
            print("Login successfull")
            return redirect('homepage')
        else:
            messages.warning(request,"Incorrect username or password")
            return redirect('userloginpage')

    response = render(request,'user/userlogsign.html')
    return HttpResponse(response)

#logout for admin and user 
def logoutuser(request):
    if request.method =='GET':
        logout(request)
        messages.success(request,"Logged out successfully")
        print("Logged out successfully")
        return redirect('homepage')
    else:
        print("logout unsuccessfull")
        return redirect('userloginpage')

#staff login and signup page
def staff_log_sign_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username,password=password)
        
        if user.is_staff:
            login(request,user)
            return redirect('staffpanel')
        
        else:
            messages.success(request,"Incorrect username or password")
            return redirect('staffloginpage')
    response = render(request,'staff/stafflogsign.html')
    return HttpResponse(response)

#staff panel page
@login_required(login_url='/staff')
def panel(request):
    
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    
    rooms = Rooms.objects.all()
    total_rooms = len(rooms)
    available_rooms = len(Rooms.objects.all().filter(status='1'))
    unavailable_rooms = len(Rooms.objects.all().filter(status='2'))
    reserved = len(Reservation.objects.all())

    hotel = Hotels.objects.values_list('location','id').distinct().order_by()

    response = render(request,'staff/panel.html',{'location':hotel,'reserved':reserved,'rooms':rooms,'total_rooms':total_rooms,'available':available_rooms,'unavailable':unavailable_rooms})
    return HttpResponse(response)

#for editing room information
@login_required(login_url='/staff')
def edit_room(request):
    if request.user.is_staff == False:   
        return HttpResponse('Access Denied')
    if request.method == 'POST' and request.user.is_staff:
        print(request.POST)
        old_room = Rooms.objects.all().get(id= int(request.POST['roomid']))
        hotel = Hotels.objects.all().get(id=int(request.POST['hotel']))
        old_room.room_type  = request.POST['roomtype']
        old_room.capacity   =int(request.POST['capacity'])
        old_room.price      = int(request.POST['price'])
        old_room.size       = int(request.POST['size'])
        old_room.hotel      = hotel
        old_room.status     = request.POST['status']
        old_room.room_number=int(request.POST['roomnumber'])

        old_room.save()
        messages.success(request,"Room Details Updated Successfully")
        return redirect('staffpanel')
    else:
    
        room_id = request.GET['roomid']
        room = Rooms.objects.all().get(id=room_id)
        response = render(request,'staff/editroom.html',{'room':room})
        return HttpResponse(response)

#for adding room
@login_required(login_url='/staff')
def add_new_room(request):
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    if request.method == "POST":
        total_rooms = len(Rooms.objects.all())
        new_room = Rooms()
        hotel = Hotels.objects.all().get(id = int(request.POST['hotel']))
        print(f"id={hotel.id}")
        print(f"name={hotel.name}")


        new_room.roomnumber = total_rooms + 1
        new_room.room_type  = request.POST['roomtype']
        new_room.capacity   = int(request.POST['capacity'])
        new_room.size       = int(request.POST['size'])
        new_room.capacity   = int(request.POST['capacity'])
        new_room.hotel      = hotel
        new_room.status     = request.POST['status']
        new_room.price      = request.POST['price']

        new_room.save()
        messages.success(request,"New Room Added Successfully")
    
    return redirect('staffpanel')

#booking room page
@login_required(login_url='/user')
def book_room_page(request):
    room = Rooms.objects.all().get(id=int(request.GET['roomid']))
    print("room...........", room)
    return HttpResponse(render(request,'user/bookroom.html',{'room':room}))

#For booking the room
@login_required(login_url='/user')
def book_room(request):
    
    if request.method =="POST":

        room_id = request.POST['room_id']
        
        room = Rooms.objects.all().get(id=room_id)
        print("room............", room)
        #for finding the reserved rooms on this time period for excluding from the query set
        for each_reservation in Reservation.objects.all().filter(room = room):
            if str(each_reservation.check_in) < str(request.POST['check_in']) and str(each_reservation.check_out) < str(request.POST['check_out']):
                pass
            elif str(each_reservation.check_in) > str(request.POST['check_in']) and str(each_reservation.check_out) > str(request.POST['check_out']):
                pass
            else:
                messages.warning(request,"Sorry This Room is unavailable for Booking")
                return redirect("homepage")
            
        current_user = request.user
        total_person = int( request.POST['person'])
        booking_id = str(room_id) + str(datetime.datetime.now())

        reservation = Reservation()
        room_object = Rooms.objects.all().get(id=room_id)
        room_object.status = '2'
        
        user_object = User.objects.all().get(username=current_user)

        reservation.guest = user_object
        reservation.room = room_object
        person = total_person
        reservation.check_in = request.POST['check_in']
        reservation.check_out = request.POST['check_out']

        reservation.save()

        # messages.success(request,"Congratulations! Booking Successfull")

        return render(request, 'payment.html')
    else:
        return HttpResponse('Access Denied')

logger = logging.getLogger(__name__)
@login_required(login_url='/user')
def payment_view(request):
    print("request.method///////////////////////", request.method)
    print("request..................", request)
    if request.method == "POST":
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        card_name = request.POST.get('card_name')
        print("card number, expiry date, card name........................", card_name, card_number, expiry_date)

        logger.debug(f"Received payment data: card_number={card_number}, expiry_date={expiry_date}, card_name={card_name}")

        if not card_number or not expiry_date or not card_name:
            messages.error(request, "Please fill in all required fields.")
            return redirect('payment_view')

        # Create a new Payment object
        payment = Payment(
            user=request.user,
            card_number=card_number,
            expiry_date=expiry_date,
            card_name=card_name
        )
        print("payment]]]]]]]]]]]]]]]]]]]", payment)
        payment.save()
        
        messages.success(request, "Congratulations! Booking Successful.")
        return redirect('homepage')

    return render(request, 'payment.html')

def handler404(request):
    return render(request, '404.html', status=404)

@login_required(login_url='/staff')   
def view_room(request):
    room_id = request.GET['roomid']
    room = Rooms.objects.all().get(id=room_id)

    reservation = Reservation.objects.all().filter(room=room)
    return HttpResponse(render(request,'staff/viewroom.html',{'room':room,'reservations':reservation}))

@login_required(login_url='/user')
def user_bookings(request):
    if request.user.is_authenticated == False:
        return redirect('userloginpage')
    user = User.objects.all().get(id=request.user.id)
    print(f"request user id ={request.user.id}")
    bookings = Reservation.objects.all().filter(guest=user)
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return HttpResponse(render(request,'user/mybookings.html',{'bookings':bookings}))

@login_required(login_url='/staff')
def add_new_location(request):
    if request.method == "POST" and request.user.is_staff:
        owner = request.POST['new_owner']
        location = request.POST['new_city']
        state = request.POST['new_state']
        country = request.POST['new_country']
        description = request.POST['description']

        # Check if a hotel at the given location and state already exists
        hotels = Hotels.objects.all().filter(location=location, state=state)
        if hotels:
            messages.warning(request, "Sorry, a city at this location already exists.")
            return redirect("staffpanel")
        else:
            new_hotel = Hotels(
                owner=owner,
                location=location,
                state=state,
                country=country,
                description=description,
                image_1=request.FILES.get('image_1'),
                image_2=request.FILES.get('image_2'),
                image_3=request.FILES.get('image_3')
            )
            new_hotel.save()
            messages.success(request, "New Location Has Been Added Successfully")
            return redirect("staffpanel")
    else:
        return HttpResponse("Not Allowed")

    
#for showing all bookings to staff
@login_required(login_url='/staff')
def all_bookings(request):
   
    bookings = Reservation.objects.all()
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return HttpResponse(render(request,'staff/allbookings.html',{'bookings':bookings}))
    


        