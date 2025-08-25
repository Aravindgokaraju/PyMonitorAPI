import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from pymongo import MongoClient
import sys  # For printing full exception info

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for databases...')
        db_conn = None
        while not db_conn:
            try:
                # Check MySQL
                connections['default'].ensure_connection()
                # Check MongoDB (if using PyMongo)
                MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=1000).admin.command('ping')
                db_conn = True
            except OperationalError as e:
                self.stdout.write(self.style.ERROR(f'MySQL connection failed: {str(e)}'))
                self.stdout.write(f'Full exception: {sys.exc_info()}')  # Prints full traceback
                time.sleep(1)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'MongoDB connection failed: {str(e)}'))
                self.stdout.write(f'Full exception: {sys.exc_info()}')  # Prints full traceback
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Databases ready!'))