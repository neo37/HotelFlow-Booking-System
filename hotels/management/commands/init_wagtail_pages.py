from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from pages.models import HomePage, ContactPage


class Command(BaseCommand):
    help = 'Инициализирует структуру страниц Wagtail'

    def handle(self, *args, **options):
        self.stdout.write('Инициализация страниц Wagtail...')
        
        root = Page.get_first_root_node()
        if not root:
            self.stdout.write(self.style.ERROR('Корневая страница не найдена!'))
            return
        
        # Проверяем, есть ли уже дочерние страницы
        children = root.get_children()
        
        # Если нет дочерних страниц, создаем первую страницу с явным указанием пути
        if not children.exists():
            self.stdout.write('Создание первой страницы...')
            
            # Создаем главную страницу
            home_page = HomePage(
                title='Добро пожаловать в наши гостиницы',
                slug='home',
                body=[
                    {
                        'type': 'heading',
                        'value': 'Добро пожаловать!'
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Мы рады приветствовать вас в нашей сети гостиниц. Мы предлагаем комфортабельные номера, отличный сервис и незабываемые впечатления от отдыха.</p>'
                    },
                    {
                        'type': 'heading',
                        'value': 'Наши преимущества'
                    },
                    {
                        'type': 'paragraph',
                        'value': '<ul><li>Удобное расположение в центре города</li><li>Современные номера с всеми удобствами</li><li>Профессиональный персонал</li><li>Лучшие цены на рынке</li></ul>'
                    },
                ]
            )
            
            # Устанавливаем путь вручную для первой страницы
            home_page.path = root.path + '0001'
            home_page.depth = root.depth + 1
            home_page.numchild = 0
            home_page.save()
            
            # Обновляем root
            root.numchild = 1
            root.save()
            
            # Публикуем страницу
            home_page.save_revision().publish()
            
            # Создаем или обновляем сайт
            site = Site.objects.first()
            if not site:
                site = Site.objects.create(
                    hostname='localhost',
                    port=8000,
                    site_name='Гостиничный бизнес',
                    root_page=home_page,
                    is_default_site=True
                )
                self.stdout.write(self.style.SUCCESS('✅ Сайт создан'))
            else:
                site.root_page = home_page
                site.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Главная страница создана'))
            
            # Теперь создаем страницу контактов
            contact_page = ContactPage(
                title='Контакты',
                slug='contacts',
                address='Москва, ул. Примерная, д. 1',
                phone='+7 (495) 123-45-67',
                email='info@hotels.ru',
                body=[
                    {
                        'type': 'heading',
                        'value': 'Свяжитесь с нами'
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Мы всегда рады ответить на ваши вопросы и помочь с бронированием.</p>'
                    },
                    {
                        'type': 'paragraph',
                        'value': '<p>Работаем круглосуточно, 7 дней в неделю.</p>'
                    },
                ]
            )
            
            contact_page.path = root.path + '0002'
            contact_page.depth = root.depth + 1
            contact_page.numchild = 0
            contact_page.save()
            
            root.numchild = 2
            root.save()
            
            contact_page.save_revision().publish()
            
            self.stdout.write(self.style.SUCCESS('✅ Страница контактов создана'))
        else:
            self.stdout.write(self.style.WARNING('Страницы уже существуют. Пропускаем создание.'))
        
        # Убеждаемся, что Site настроен правильно
        site = Site.objects.first()
        home_page = HomePage.objects.filter(slug='home').first()
        
        if home_page:
            if not site:
                site = Site.objects.create(
                    hostname='localhost',
                    port=8000,
                    site_name='Гостиничный бизнес',
                    root_page=home_page,
                    is_default_site=True
                )
                self.stdout.write(self.style.SUCCESS('✅ Сайт создан'))
            elif site.root_page != home_page:
                site.root_page = home_page
                site.save()
                self.stdout.write(self.style.SUCCESS('✅ Корневая страница сайта обновлена'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Инициализация завершена!'))

