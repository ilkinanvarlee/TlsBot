from django.core.management.base import BaseCommand
from tlsbot.bot import TLSBot


class Command(BaseCommand):
    help = 'TLSContact botunu işə salır'

    def handle(self, *args, **kwargs):
        print("Bot command ilə işə salındı...")
        bot = TLSBot()
        bot.run()
        print("✅ Bot icra olundu.")

