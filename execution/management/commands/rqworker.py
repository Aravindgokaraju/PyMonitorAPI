# from django.core.management.base import BaseCommand
# from django_rq.workers import get_worker

# class Command(BaseCommand):
#     help = 'Starts RQ worker for scraping tasks'

#     def add_arguments(self, parser):
#         parser.add_argument('queues', nargs='*', type=str, default=['scraping'])

#     def handle(self, *args, **options):
#         queues = options['queues']
#         worker = get_worker(*queues)
        
#         self.stdout.write(
#             self.style.SUCCESS(f'Starting worker for queues: {queues}')
#         )
        
#         worker.work()