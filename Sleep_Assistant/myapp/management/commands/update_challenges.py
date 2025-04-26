from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.sleep_challenge_views import update_challenge_status
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update challenge statuses (mark expired challenges as inactive)'

    def handle(self, *args, **options):
        try:
            self.stdout.write("Starting challenge status update...")
            
            success = update_challenge_status()
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('Successfully updated challenge statuses')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to update challenge statuses')
                )
                
        except Exception as e:
            logger.error(f"Error updating challenge statuses: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Error updating challenge statuses: {str(e)}')
            )
