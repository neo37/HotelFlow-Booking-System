from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Hotel, Room, Booking
from .forms import BookingForm, DateFilterForm


def hotel_list(request):
    """Список гостиниц с фильтрацией по датам"""
    form = DateFilterForm(request.GET)
    hotels = Hotel.objects.all()
    
    check_in = None
    check_out = None
    
    if form.is_valid():
        check_in = form.cleaned_data.get('check_in')
        check_out = form.cleaned_data.get('check_out')
        
        if check_in and check_out:
            # Находим гостиницы, у которых есть свободные номера в указанные даты
            booked_room_ids = Booking.objects.filter(
                Q(check_in__lt=check_out) & Q(check_out__gt=check_in),
                status__in=['pending', 'confirmed']
            ).values_list('room_id', flat=True)
            
            hotels_with_rooms = Room.objects.exclude(
                id__in=booked_room_ids
            ).values_list('hotel_id', flat=True).distinct()
            
            hotels = hotels.filter(id__in=hotels_with_rooms)
    
    context = {
        'hotels': hotels,
        'form': form,
        'check_in': check_in,
        'check_out': check_out,
    }
    return render(request, 'hotels/hotel_list.html', context)


def room_list(request, hotel_id):
    """Список номеров в гостинице с фильтрацией по датам"""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    form = DateFilterForm(request.GET)
    rooms = hotel.rooms.all()
    
    check_in = None
    check_out = None
    
    if form.is_valid():
        check_in = form.cleaned_data.get('check_in')
        check_out = form.cleaned_data.get('check_out')
        
        if check_in and check_out:
            # Находим забронированные номера в указанные даты
            booked_room_ids = Booking.objects.filter(
                Q(check_in__lt=check_out) & Q(check_out__gt=check_in),
                status__in=['pending', 'confirmed']
            ).values_list('room_id', flat=True)
            
            rooms = rooms.exclude(id__in=booked_room_ids)
    
    context = {
        'hotel': hotel,
        'rooms': rooms,
        'form': form,
        'check_in': check_in,
        'check_out': check_out,
    }
    return render(request, 'hotels/room_list.html', context)


def room_detail(request, room_id):
    """Детальная информация о номере и форма бронирования"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room
            
            # Проверяем, свободен ли номер в указанные даты
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            
            conflicting_bookings = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=['pending', 'confirmed']
            )
            
            if conflicting_bookings.exists():
                messages.error(request, 'К сожалению, номер уже забронирован на указанные даты.')
            else:
                booking.save()
                messages.success(request, 'Ваша заявка на бронирование успешно отправлена! Мы свяжемся с вами в ближайшее время.')
                return redirect('hotels:room_detail', room_id=room.id)
    else:
        form = BookingForm()
    
    context = {
        'room': room,
        'form': form,
    }
    return render(request, 'hotels/room_detail.html', context)

