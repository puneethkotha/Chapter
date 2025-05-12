from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from library.models import Event, Exhibition, Seminar

class Command(BaseCommand):
    help = 'Adds new events to the database'

    def handle(self, *args, **kwargs):
        # Get the next available event ID
        try:
            max_id = Event.objects.order_by('-event_id').first().event_id
        except AttributeError:
            max_id = 0

        # Create some exhibitions
        exhibitions = [
            {
                'name': 'Summer Book Fair 2024',
                'start_dt': timezone.now() + timedelta(days=2),
                'end_dt': timezone.now() + timedelta(days=3),
                'attd_no': 100,
                'expenses': 5000.00
            },
            {
                'name': 'Children\'s Literature Exhibition',
                'start_dt': timezone.now() + timedelta(days=5),
                'end_dt': timezone.now() + timedelta(days=6),
                'attd_no': 75,
                'expenses': 3000.00
            },
            {
                'name': 'Science Fiction Book Showcase',
                'start_dt': timezone.now() + timedelta(days=8),
                'end_dt': timezone.now() + timedelta(days=9),
                'attd_no': 120,
                'expenses': 6000.00
            }
        ]

        # Create some seminars
        seminars = [
            {
                'name': 'Writing Workshop with Best-Selling Authors',
                'start_dt': timezone.now() + timedelta(days=3),
                'end_dt': timezone.now() + timedelta(days=3, hours=4),
                'attd_no': 50,
                'est_auth': 3
            },
            {
                'name': 'Digital Publishing Trends',
                'start_dt': timezone.now() + timedelta(days=7),
                'end_dt': timezone.now() + timedelta(days=7, hours=3),
                'attd_no': 40,
                'est_auth': 2
            }
        ]

        # Create exhibitions
        for exhibition_data in exhibitions:
            event_id = max_id + 1
            max_id += 1
            
            # Create event
            event = Event.objects.create(
                event_id=event_id,
                event_name=exhibition_data['name'],
                start_dt=exhibition_data['start_dt'],
                end_dt=exhibition_data['end_dt'],
                attd_no=exhibition_data['attd_no'],
                event_type='E'
            )
            
            # Create exhibition
            Exhibition.objects.create(
                event=event,
                expenses=exhibition_data['expenses']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created exhibition: {exhibition_data["name"]}')
            )

        # Create seminars
        for seminar_data in seminars:
            event_id = max_id + 1
            max_id += 1
            
            # Create event
            event = Event.objects.create(
                event_id=event_id,
                event_name=seminar_data['name'],
                start_dt=seminar_data['start_dt'],
                end_dt=seminar_data['end_dt'],
                attd_no=seminar_data['attd_no'],
                event_type='S'
            )
            
            # Create seminar
            Seminar.objects.create(
                event=event,
                est_auth=seminar_data['est_auth']
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created seminar: {seminar_data["name"]}')
            ) 