from django.core.management.base import BaseCommand
from django.utils import timezone
from library.models import Event, Exhibition, Customer, ExhibitionAttendance

class Command(BaseCommand):
    help = 'Fills up an exhibition with test registrations'

    def handle(self, *args, **options):
        # Get the first upcoming exhibition
        now = timezone.now()
        exhibition_event = Event.objects.filter(
            event_type='E',
            end_dt__gt=now
        ).order_by('start_dt').first()

        if not exhibition_event:
            self.stdout.write(self.style.ERROR('No upcoming exhibitions found'))
            return

        exhibition = Exhibition.objects.get(event=exhibition_event)
        current_attendees = exhibition.attendees.count()
        capacity = exhibition_event.attd_no

        if current_attendees >= capacity:
            self.stdout.write(self.style.SUCCESS(f'Exhibition "{exhibition_event.event_name}" is already full ({current_attendees}/{capacity})'))
            return

        # Get all customers
        customers = Customer.objects.all()
        if not customers:
            self.stdout.write(self.style.ERROR('No customers found in the database'))
            return

        # Register customers until capacity is reached
        registrations_needed = capacity - current_attendees
        registrations_made = 0

        for customer in customers:
            if registrations_made >= registrations_needed:
                break

            # Check if customer is already registered
            if not exhibition.attendees.filter(cust_id=customer.cust_id).exists():
                ExhibitionAttendance.objects.create(
                    exhibition=exhibition,
                    customer=customer
                )
                registrations_made += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully registered {registrations_made} customers for "{exhibition_event.event_name}"\n'
            f'Current attendance: {current_attendees + registrations_made}/{capacity}'
        )) 