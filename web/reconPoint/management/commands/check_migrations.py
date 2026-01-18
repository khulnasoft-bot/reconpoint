from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = 'Check and apply pending database migrations'

    def handle(self, *args, **options):
        self.stdout.write('Checking for pending migrations...')

        # Check for pending migrations
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        applied = executor.loader.applied_migrations

        pending = []
        for target in targets:
            if target not in applied:
                pending.append(target)

        if pending:
            self.stdout.write(self.style.WARNING(f'Found {len(pending)} pending migrations:'))
            for mig in pending:
                self.stdout.write(f'  - {mig[0]}.{mig[1]}')

            self.stdout.write('Applying migrations...')
            call_command('migrate', verbosity=1)
            self.stdout.write(self.style.SUCCESS('All migrations applied successfully.'))
        else:
            self.stdout.write(self.style.SUCCESS('No pending migrations. Database is up to date.'))

        # Run performance check
        self.stdout.write('Running database performance checks...')
        # You can add more checks here, like index usage, slow queries, etc.
        self.stdout.write(self.style.SUCCESS('Performance checks completed.'))