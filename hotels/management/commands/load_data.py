from django.core.management.base import BaseCommand
from hotels.models import Hotel, HotelImage, Room, Booking
from pages.models import HomePage, ContactPage, HotelPage
from wagtail.models import Site, Page
from datetime import date, timedelta
import random
import re


def create_slug(text):
    """Создает slug из текста с транслитерацией кириллицы"""
    # Простая транслитерация
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
    }
    
    text = text.lower()
    result = ''
    for char in text:
        if char in translit_map:
            result += translit_map[char]
        elif char.isalnum() or char == '-':
            result += char
        else:
            result += '-'
    
    # Убираем множественные дефисы
    result = re.sub(r'-+', '-', result)
    result = result.strip('-')
    
    return result


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        # Создаем гостиницы
        hotels_data = [
            {
                'name': 'Гранд Отель Москва',
                'description': 'Роскошный отель в центре Москвы с видом на Кремль. Современные номера, ресторан высокой кухни и спа-центр.',
                'address': 'Москва, ул. Тверская, д. 1'
            },
            {
                'name': 'Морской Бриз',
                'description': 'Курортный отель на берегу Черного моря. Пляж, бассейн, ресторан с морепродуктами.',
                'address': 'Сочи, ул. Приморская, д. 25'
            },
            {
                'name': 'Северное Сияние',
                'description': 'Уютный отель в Санкт-Петербурге. Близко к Эрмитажу и Невскому проспекту.',
                'address': 'Санкт-Петербург, Невский проспект, д. 50'
            },
        ]
        
        hotels = []
        for hotel_data in hotels_data:
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data['name'],
                defaults=hotel_data
            )
            hotels.append(hotel)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана гостиница: {hotel.name}'))
        
        # Создаем номера для каждой гостиницы
        room_types = [
            {'name': 'Стандартный номер', 'area': 25.0, 'price': 3000, 'desc': 'Уютный номер с одной кроватью, телевизором и мини-баром.'},
            {'name': 'Улучшенный номер', 'area': 35.0, 'price': 4500, 'desc': 'Просторный номер с видом, кондиционером и рабочим местом.'},
            {'name': 'Люкс', 'area': 50.0, 'price': 7000, 'desc': 'Роскошный номер с гостиной зоной, джакузи и панорамным видом.'},
            {'name': 'Президентский люкс', 'area': 80.0, 'price': 12000, 'desc': 'Эксклюзивный номер с отдельной гостиной, столовой и персональным дворецким.'},
            {'name': 'Семейный номер', 'area': 45.0, 'price': 6000, 'desc': 'Просторный номер для семьи с двумя спальнями и детской зоной.'},
        ]
        
        for hotel in hotels:
            for i, room_type in enumerate(room_types[:3]):  # По 3 номера каждого типа
                room, created = Room.objects.get_or_create(
                    hotel=hotel,
                    name=f"{room_type['name']} {i+1}",
                    defaults={
                        'description': room_type['desc'],
                        'area': room_type['area'],
                        'price_per_night': room_type['price'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Создан номер: {room.name} в {hotel.name}'))
        
        # Создаем страницы гостиниц в Wagtail
        root = Page.get_first_root_node()
        if root:
            for hotel in hotels:
                # Проверяем, есть ли уже страница для этой гостиницы
                existing_page = HotelPage.objects.filter(hotel=hotel).first()
                
                if not existing_page:
                    # Создаем страницу гостиницы
                    slug = create_slug(hotel.name)
                    # Проверяем уникальность slug
                    counter = 1
                    original_slug = slug
                    while HotelPage.objects.filter(slug=slug).exists():
                        slug = f"{original_slug}-{counter}"
                        counter += 1
                    
                    hotel_page = HotelPage(
                        title=hotel.name,
                        slug=slug,
                        hotel=hotel,
                    )
                    
                    # Пытаемся добавить как дочернюю страницу к корню или к главной
                    home_page = HomePage.objects.filter(slug='home').first()
                    parent = home_page if home_page else root
                    
                    try:
                        parent.add_child(instance=hotel_page)
                        hotel_page.save_revision().publish()
                        self.stdout.write(self.style.SUCCESS(f'Создана страница Wagtail для: {hotel.name}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Не удалось создать страницу для {hotel.name}: {e}'))
        
        # Создаем несколько бронирований
        rooms = Room.objects.all()
        if rooms.exists():
            for i in range(5):
                room = random.choice(rooms)
                check_in = date.today() + timedelta(days=random.randint(10, 30))
                check_out = check_in + timedelta(days=random.randint(1, 5))
                
                booking = Booking.objects.create(
                    room=room,
                    guest_name=f'Гость {i+1}',
                    guest_email=f'guest{i+1}@example.com',
                    guest_phone=f'+7 999 123-{45+i:02d}-67',
                    check_in=check_in,
                    check_out=check_out,
                    status=random.choice(['pending', 'confirmed'])
                )
                self.stdout.write(self.style.SUCCESS(f'Создано бронирование: {booking}'))
        
        # Создаем главную страницу Wagtail
        from wagtail.models import Page
        
        root = Page.get_first_root_node()
        if root:
            # Проверяем, есть ли уже главная страница HomePage
            existing_home = HomePage.objects.filter(slug='home').first()
            
            if existing_home:
                # Обновляем существующую страницу
                home_page = existing_home
                home_page.title = 'Добро пожаловать в наши гостиницы'
            else:
                # Проверяем, есть ли дефолтная страница Wagtail
                default_home = root.get_children().filter(slug='home').first()
                if default_home:
                    # Преобразуем дефолтную страницу в HomePage
                    default_home.delete()
                
                # Создаем новую главную страницу
                home_page = HomePage(
                    title='Добро пожаловать в наши гостиницы',
                    slug='home',
                )
                try:
                    root.add_child(instance=home_page)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Ошибка при создании страницы: {e}'))
                    # Пробуем найти существующую
                    home_page = root.get_children().filter(slug='home').first()
                    if not home_page:
                        return
            
            # Создаем StreamField контент
            home_page.body = [
                ('heading', 'Добро пожаловать!'),
                ('paragraph', '<p>Мы рады приветствовать вас в нашей сети гостиниц. Мы предлагаем комфортабельные номера, отличный сервис и незабываемые впечатления от отдыха.</p>'),
                ('heading', 'Наши преимущества'),
                ('paragraph', '<ul><li>Удобное расположение в центре города</li><li>Современные номера с всеми удобствами</li><li>Профессиональный персонал</li><li>Лучшие цены на рынке</li></ul>'),
            ]
            
            home_page.save()
            home_page.save_revision().publish()
            
            # Обновляем сайт
            site = Site.objects.first()
            if site:
                site.root_page = home_page
                site.save()
            
            self.stdout.write(self.style.SUCCESS('Создана/обновлена главная страница Wagtail'))
        
        # Создаем страницу контактов
        if root:
            existing_contact = ContactPage.objects.filter(slug='contacts').first()
            
            if existing_contact:
                contact_page = existing_contact
            else:
                contact_page = ContactPage(
                    title='Контакты',
                    slug='contacts',
                )
                try:
                    root.add_child(instance=contact_page)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Ошибка при создании страницы контактов: {e}'))
                    return
            
            contact_page.address = 'Москва, ул. Примерная, д. 1'
            contact_page.phone = '+7 (495) 123-45-67'
            contact_page.email = 'info@hotels.ru'
            
            contact_page.body = [
                ('heading', 'Свяжитесь с нами'),
                ('paragraph', '<p>Мы всегда рады ответить на ваши вопросы и помочь с бронированием.</p>'),
                ('paragraph', '<p>Работаем круглосуточно, 7 дней в неделю.</p>'),
            ]
            
            contact_page.save()
            contact_page.save_revision().publish()
            
            self.stdout.write(self.style.SUCCESS('Создана/обновлена страница контактов'))
        
        # Инициализируем страницы Wagtail
        self.stdout.write('\nИнициализация страниц Wagtail...')
        from django.core.management import call_command
        call_command('init_wagtail_pages')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Все данные успешно загружены!'))
        self.stdout.write(self.style.SUCCESS('\n📝 Данные для входа:'))
        self.stdout.write(self.style.SUCCESS('   Логин: admin'))
        self.stdout.write(self.style.SUCCESS('   Пароль: admin123'))

