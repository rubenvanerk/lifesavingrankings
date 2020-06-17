from django.core.management.base import BaseCommand

from rankings.functions import calculate_fina_points
from rankings.models import IndividualResult, EventRecord, Athlete


class Command(BaseCommand):
    help = "Recalculates points"

    def handle(self, *args, **options):
        events = EventRecord.objects.distinct('event').values_list('event__pk', flat=True)
        results = IndividualResult.public_objects.only_valid_results().filter(event__in=events).select_related('athlete')
        event_records = EventRecord.objects.all()
        record_mappings = {Athlete.MALE: {}, Athlete.FEMALE: {}}
        for event_record in event_records:
            record_mappings[event_record.gender][event_record.event.pk] = event_record

        count = 0
        total = results.count()
        for result in results:
            count += 1
            event_record = record_mappings[result.athlete.gender][result.event.pk]
            result.points = calculate_fina_points(event_record.time.total_seconds() * 100, result.time.total_seconds() * 100)
            result.save()
            if count % 100 == 0:
                self.stdout.write(f"Calculated {count}/{total} results")


