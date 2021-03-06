# -*- coding:utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from core.models import TimeStampedModel
from .managers import ActiveManager


class Partner(models.Model):
    description = models.CharField(_(u'Descrição'), max_length=100)
    url = models.URLField(_('URL'))
    logo = models.ImageField(upload_to='uploads/partners')

    class Meta:
        verbose_name = _(u'Parceiro')
        verbose_name_plural = _(u'Parceiros')

    def __unicode__(self):
        return self.description


class Sponsor(Partner):
    TYPES = (
        ('gold', _('Ouro')),
        ('silver', _('Prata')),
        ('bronze', _('bronze')),
    )
    type = models.CharField(_('Tipo'), max_length=20, choices=TYPES)

    class Meta:
        verbose_name = _(u'Patrocinador')
        verbose_name_plural = _(u'Patrocinadores')


class Support(Partner):

    class Meta:
        verbose_name = _(u'Apoio')
        verbose_name_plural = _(u'Apoio')


class Event(TimeStampedModel):
    description = models.CharField(_(u'Descrição'), max_length=100)
    full_description = models.TextField(_(u'Descrição Completa'))
    date = models.DateTimeField(_(u'Data'))
    slug = models.SlugField()
    location = models.ForeignKey(
        'geo.Location', verbose_name=_(u'Local'), null=True, blank=True,
    )
    partners = models.ManyToManyField(
        'events.Partner', verbose_name=_(u'Parceiros'),
        null=True, blank=True,
    )
    submission_deadline = models.DateTimeField(
        _(u'Data limite para submissão'),
    )
    index = models.BooleanField(
        help_text=u'Indica que a raiz do site irá redirecionar para esse '
        u'evento. ex: Ao entrar em pycon.pug.pe/ redireciona para pycon.'
        u'pug.pe/slug_definido',
    )
    signature = models.ForeignKey(
        'cert.Signature', verbose_name=_(u'Assinatura'),
        help_text=_(u'Assinatura a ser usada nos certificados'),
        null=True,
    )

    length = models.PositiveIntegerField(
        _(u'Duração do evento'), help_text=_(u'Utilizada em certificado'),
    )

    # When used, the event page will be redirected to the specifyed link
    external_link = models.CharField(
        _(u'Link Externo'), max_length=200, blank=True,
        help_text=_(
            u'Quando utilizado, o evento será redirecionado para a'
            u' url. <br />Utilizado para manter a seção Arquivo atualizada, '
            u'mesmo para eventos hospedados em hosts externos')
    )

    class Meta:
        verbose_name = _(u'Evento')
        verbose_name_plural = _(u'Eventos')

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self._original_index = self.index

    def __unicode__(self):
        return self.description

    def save(self, *args, **kwargs):
        # Caso marcado index, desmarcar outros.
        if self.index and self.index != self._original_index:
            Event.objects.exclude(pk=self.pk).update(index=False)

        super(Event, self).save(*args, **kwargs)
        self._original_index = self.index

    def get_absolute_url(self):
        if not self.external_link:
            return reverse('events:event', kwargs={'event_slug': self.slug})
        else:
            return self.external_link


class EventTalk(TimeStampedModel):
    '''
    Meta dados de palestra no evento, afim de facilitar cadastro das palestras
    no evento
    '''
    status = models.BooleanField(_(u'Ativo'))

    event = models.ForeignKey('events.Event', verbose_name=_(u'Evento'))
    talk = models.ForeignKey(
        'submission.Talk', verbose_name=_(u'Palestra'), null=True, blank=True,
    )

    start = models.TimeField(_(u'Início'), null=True, blank=True)
    end = models.TimeField(_(u'Fim'), null=True, blank=True)

    title = models.CharField(
        _(u'Título'), max_length=80, null=True, blank=True,
        help_text=_(u'Preencher para quando não há uma palestra relacionada '
                    u'ou para sobrescrever título de palestra'),
    )

    objects = models.Manager()
    active = ActiveManager()

    def __unicode__(self):
        return u'{0} - {1}'.format(self.event, self.talk)

    def get_title(self):
        return self.title if self.title else self.talk.title

    def get_name(self):
        return self.talk.name if self.talk else ''
