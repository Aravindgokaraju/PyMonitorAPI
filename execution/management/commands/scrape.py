from django.core.management.base import BaseCommand
from execution.scraping.scrape_website import ScrapingService

class Command(BaseCommand):
    help = 'Run the web scraping process'

    def handle(self, *args, **options):
        scraper = ScrapingService()
        results = scraper.scrape_websites()
        self.stdout.write(self.style.SUCCESS(f'Successfully scraped {len(results)} items'))