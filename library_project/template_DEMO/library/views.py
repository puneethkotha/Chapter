@customer_required
def my_reservations(request):
    """Display user's study room reservations"""
    now = timezone.now()
    
    # Get all reservations for the user
    all_reservations = Reservation.objects.filter(
        customer=request.user.customer_profile
    ).select_related('study_room').order_by('-start_dt')
    
    # Split into upcoming and past reservations
    upcoming_reservations = []
    past_reservations = []
    
    for reservation in all_reservations:
        if reservation.start_dt >= now:
            upcoming_reservations.append(reservation)
        else:
            past_reservations.append(reservation)
    
    context = {
        'upcoming_reservations': upcoming_reservations,
        'past_reservations': past_reservations
    }
    return render(request, 'library/my_reservations.html', context) 