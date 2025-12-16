from django.db import models
from django.core.validators import MinValueValidator


class Hotel(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    address = models.CharField(max_length=300, verbose_name='Адрес')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Гостиница'
        verbose_name_plural = 'Гостиницы'
        ordering = ['name']

    def __str__(self):
        return self.name


class HotelImage(models.Model):
    """Фотографии гостиницы для галереи"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='gallery_images', verbose_name='Гостиница')
    image = models.ImageField(upload_to='hotels/gallery/', verbose_name='Фото')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Подпись')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Фото гостиницы'
        verbose_name_plural = 'Фото гостиницы'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.hotel.name} - {self.caption or 'Фото'}"


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms', verbose_name='Гостиница')
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    area = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Площадь (м²)')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Цена за ночь')
    photo = models.ImageField(upload_to='rooms/', blank=True, null=True, verbose_name='Фото')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        ordering = ['hotel', 'name']

    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name='Номер')
    guest_name = models.CharField(max_length=200, verbose_name='Имя гостя')
    guest_email = models.EmailField(verbose_name='Email гостя')
    guest_phone = models.CharField(max_length=20, verbose_name='Телефон гостя')
    check_in = models.DateField(verbose_name='Дата заезда')
    check_out = models.DateField(verbose_name='Дата выезда')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.room} - {self.guest_name} ({self.check_in} - {self.check_out})"

