import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for databases...')
        db_conn = None
        while not db_conn:
            try:
                # Check MySQL
                connections['default'].ensure_connection()
                # Check MongoDB (if using PyMongo)
                from pymongo import MongoClient
                MongoClient('mongodb://mongodb:27017/').admin.command('ping')
                db_conn = True
            except OperationalError:
                self.stdout.write('MySQL not ready, retrying in 1s...')
                time.sleep(1)
            except Exception as e:
                self.stdout.write(f'MongoDB not ready: {e}, retrying in 1s...')
                time.sleep(1)
        self.stdout.write('Databases ready!')