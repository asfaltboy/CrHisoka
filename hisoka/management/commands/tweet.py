# coding=utf-8
import os
import random
import tweepy
import tempfile

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from hisoka.models import Fireball, FeralSpirit


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('fireball')

    def handle(self, *args, **options):

        if options['fireball'] == "orilla":
            fireball_orilla = Fireball.objects.get(nombre="OrillaLibertaria")
        elif options['fireball'] == "criptolibertad":
            fireball_orilla = Fireball.objects.get(nombre="CriptoLibertad")
        else:
            raise CommandError("No se reconocio nombre del Fireball")

        # Envia tweets de Orilla Libertaria a twitter
        access_token_twitter = os.environ['ACCESS_TOKEN_TWITTER']
        access_token_twitter_secret = os.environ['ACCESS_TOKEN_TWITTER_SECRET']
        consumer_key = os.environ['CONSUMER_KEY_TWITTER']
        consumer_secret = os.environ['CONSUMER_SECRET_TWITTER']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token_twitter, access_token_twitter_secret)
        api = tweepy.API(auth)

        # api = twitter.Api(access_token_key=access_token_twitter,
        #                   access_token_secret=access_token_twitter_secret,
        #                   consumer_key=consumer_key,
        #                   consumer_secret=consumer_secret)

        # Obtener FeralSpirits
        # Toma los 3 feralspirits con fecha de publicación más lejana, luego elige uno random
        feral_spirits = FeralSpirit.objects.filter(activo=True, eliminado=False, fireball=fireball_orilla)[:3]
        lista_ferals = [f for f in feral_spirits]
        feral_elegido = random.choice(lista_ferals)

        texto_tweet = "%s %s" % (feral_elegido.texto, feral_elegido.url)

        # Enviar Tweet
        if feral_elegido.tipo == "imagen":
            # Envia tweets de Orilla Libertaria a twitter

            with tempfile.NamedTemporaryFile(delete=True) as f:
                filename = feral_elegido.imagen.file.name
                f.write(feral_elegido.imagen.read())
                media_ids = api.media_upload(filename=filename, f=f)
                params = {'status': texto_tweet, 'media_ids': [media_ids.media_id_string]}
                api.update_status(**params)
        else:
            api.update_status(texto_tweet)

        # Aumentar contador
        # logger(logger.info("tweet enviado id: %s" % feral_elegido.id))
        feral_elegido.aumentar_contador()

        # Actualizar fecha ultimo tweet
        feral_elegido.ultima_publicacion = datetime.today()
        feral_elegido.save()
