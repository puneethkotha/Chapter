from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from library.models import Reservation, StudyRoom, Customer

class Command(BaseCommand):
    help = 'Removes all old reservations for AliceJ and adds one past and one upcoming reservation.'

    def handle(self, *args, **kwargs):
        try:
            alice = Customer.objects.get(user__username='AliceJ')
        except Customer.DoesNotExist:
            self.stdout.write(self.style.ERROR('Alice not found. Please make sure AliceJ user exists.'))
            return

        try:
            room = StudyRoom.objects.first()
            if not room:
                self.stdout.write(self.style.ERROR('No study rooms found in the database.'))
                return
        except StudyRoom.DoesNotExist:
            self.stdout.write(self.style.ERROR('No study rooms found in the database.'))
            return

        # Delete all old reservations for Alice
        deleted, _ = Reservation.objects.filter(customer=alice).delete()
        self.stdout.write(self.style.WARNING(f'Deleted {deleted} old reservations for AliceJ.'))

        # Get the next available reservation ID
        try:
            max_id = Reservation.objects.order_by('-reserve_id').first().reserve_id
        except AttributeError:
            max_id = 0

        now = timezone.now()

        # Past reservation: 2 hours ago to 1 hour ago
        past_start = now - timedelta(hours=2)
        past_end = now - timedelta(hours=1)
        Reservation.objects.create(
            reserve_id=max_id + 1,
            topic_desc="Past Study Session",
            start_dt=past_start,
            end_dt=past_end,
            group_size=2,
            customer=alice,
            study_room=room
        )

        # Upcoming reservation: 1 hour from now to 2 hours from now
        future_start = now + timedelta(hours=1)
        future_end = now + timedelta(hours=2)
        Reservation.objects.create(
            reserve_id=max_id + 2,
            topic_desc="Upcoming Study Session",
            start_dt=future_start,
            end_dt=future_end,
            group_size=3,
            customer=alice,
            study_room=room
        )

        self.stdout.write(self.style.SUCCESS('Successfully created one past and one upcoming reservation for AliceJ.')) 