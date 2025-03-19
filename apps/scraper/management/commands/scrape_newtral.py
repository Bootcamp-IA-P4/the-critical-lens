from django.core.management.base import BaseCommand, CommandError
import logging
from apps.scraper.services import ScraperService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Extracts and saves fact-checks from Newtral'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of articles to extract'
        )
        parser.add_argument(
            '--ignore-robots',
            action='store_true',
            help='Ignores robots.txt directives'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        respect_robots = not options['ignore_robots']
        
        self.stdout.write(
            self.style.NOTICE(f"Starting extraction of Newtral fact-checks (limit: {limit}, respect_robots: {respect_robots})")
        )
        
        try:
            service = ScraperService()
            total, new, updated, failed = service.scrape_newtral(
                limit=limit,
                respect_robots=respect_robots
            )
            
            # Show statistics
            self.stdout.write(self.style.SUCCESS(f"Extraction completed:"))
            self.stdout.write(f"  Total articles processed: {total}")
            self.stdout.write(f"  New articles: {new}")
            self.stdout.write(f"  Updated articles: {updated}")
            self.stdout.write(f"  Failed articles: {failed}")
            
        except Exception as e:
            logger.error(f"Error during extraction: {e}")
            raise CommandError(f"Error during extraction: {e}")
        
        self.stdout.write(self.style.SUCCESS('Extraction successfully completed'))