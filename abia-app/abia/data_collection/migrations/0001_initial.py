from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='FormSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_type', models.CharField(choices=[('migration', 'Migration Data'), ('trade', 'Trade & Commerce'), ('sports', 'Sports & Youth'), ('hotspot', 'Hotspot Monitoring'), ('returnee', 'Returnee Assessment'), ('general', 'General Data')], db_index=True, max_length=20)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('data', models.JSONField(default=dict)),
                ('source_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('ipfs_hash', models.CharField(blank=True, db_index=True, max_length=128)),
                ('synced_to_ncfrmi', models.BooleanField(default=False)),
                ('synced_to_iom', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
