import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misitio.settings')
django.setup()

from django.contrib.auth.models import User

username = 'Pedro'
email = 'pedro@pedro.com'
password = '123_Pedro' # <-- AQUÍ pon la que tú quieras

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"¡Usuario {username} creado con éxito!")
else:
    print("El usuario ya existe.")