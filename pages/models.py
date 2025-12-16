from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from hotels.models import Hotel


class YouTubeBlock(blocks.StructBlock):
    """Блок для вставки YouTube видео"""
    url = blocks.URLBlock(label="URL видео YouTube")
    caption = blocks.CharBlock(required=False, label="Подпись")
    
    class Meta:
        icon = 'media'
        label = 'YouTube видео'
        template = 'pages/blocks/youtube_block.html'


class ImageWithCaptionBlock(blocks.StructBlock):
    """Блок для изображения с подписью"""
    image = ImageChooserBlock(label="Изображение")
    caption = blocks.CharBlock(required=False, label="Подпись")
    
    class Meta:
        icon = 'image'
        label = 'Изображение с подписью'
        template = 'pages/blocks/image_with_caption.html'


class ContentStreamBlock(blocks.StreamBlock):
    """Блоки контента для страниц"""
    paragraph = blocks.RichTextBlock(label="Параграф")
    image = ImageChooserBlock(label="Изображение")
    image_with_caption = ImageWithCaptionBlock()
    youtube = YouTubeBlock()
    embed = EmbedBlock(label="Встроенный контент")
    heading = blocks.CharBlock(label="Заголовок", icon="title")
    quote = blocks.BlockQuoteBlock(label="Цитата")


class HomePage(Page):
    """Главная страница"""
    body = StreamField(ContentStreamBlock(), use_json_field=True, blank=True, verbose_name="Контент")
    
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        from hotels.models import Hotel
        context['hotels'] = Hotel.objects.all()[:6]  # Показываем первые 6 гостиниц
        return context
    
    class Meta:
        verbose_name = "Главная страница"


class ContactPage(Page):
    """Страница контактов"""
    body = StreamField(ContentStreamBlock(), use_json_field=True, blank=True, verbose_name="Контент")
    address = models.CharField(max_length=300, blank=True, verbose_name="Адрес")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    
    content_panels = Page.content_panels + [
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('address'),
            FieldPanel('phone'),
            FieldPanel('email'),
        ], heading="Контактная информация"),
    ]
    
    class Meta:
        verbose_name = "Страница контактов"


class HotelPage(Page):
    """Страница гостиницы с редактируемым контентом"""
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.PROTECT,
        related_name='pages',
        verbose_name="Гостиница"
    )
    body = StreamField(ContentStreamBlock(), use_json_field=True, blank=True, verbose_name="Контент")
    
    content_panels = Page.content_panels + [
        FieldPanel('hotel'),
        FieldPanel('body'),
    ]
    
    class Meta:
        verbose_name = "Страница гостиницы"
    
    def get_context(self, request):
        context = super().get_context(request)
        context['hotel'] = self.hotel
        context['rooms'] = self.hotel.rooms.all()
        return context

