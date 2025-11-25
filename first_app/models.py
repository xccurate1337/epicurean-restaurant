from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


class Категория(models.Model):
    название = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    описание = models.TextField(blank=True, verbose_name="Описание")
    изображение = models.CharField(max_length=500, blank=True, verbose_name="Изображение категории")
    иконка = models.CharField(max_length=50, default='🍽️', verbose_name="Иконка")
    активно = models.BooleanField(default=True, verbose_name="Активна")
    теги = models.JSONField(default=list, verbose_name="Теги категории")
    создано = models.DateTimeField(auto_now_add=True)
    обновлено = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'категории'
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['название']

    def __str__(self):
        return self.название


class Блюдо(models.Model):
    ТИП_БЛЮДА = [
        ('закуска', 'Закуска'),
        ('салат', 'Салат'),
        ('суп', 'Суп'),
        ('основное', 'Основное блюдо'),
        ('десерт', 'Десерт'),
        ('напиток', 'Напиток'),
    ]

    УРОВЕНЬ_ОСТРОТЫ = [
        (0, 'Не острое'),
        (1, 'Слабо острое'),
        (2, 'Средне острое'),
        (3, 'Острое'),
        (4, 'Очень острое')
    ]

    категория = models.ForeignKey(Категория, on_delete=models.CASCADE, related_name='блюда')
    тип_блюда = models.CharField(max_length=20, choices=ТИП_БЛЮДА, default='основное')
    название = models.CharField(max_length=200, verbose_name="Название блюда")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    описание = models.TextField(blank=True, verbose_name="Описание")
    цена = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    изображение = models.CharField(max_length=500, blank=True, verbose_name="Ссылка на изображение")
    вес_объем = models.CharField(max_length=50, verbose_name="Вес/Объем")
    состав = models.TextField(verbose_name="Состав")
    пищевая_ценность = models.JSONField(default=dict, verbose_name="Пищевая ценность")
    время_приготовления = models.PositiveIntegerField(default=15, verbose_name="Время приготовления (мин)")
    уровень_остроты = models.PositiveIntegerField(choices=УРОВЕНЬ_ОСТРОТЫ, default=0)
    теги = models.JSONField(default=list)
    активно = models.BooleanField(default=True)
    акция = models.BooleanField(default=False)
    цена_со_скидкой = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    популярность = models.IntegerField(default=0)
    создано = models.DateTimeField(auto_now_add=True)
    обновлено = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'блюда'
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ['-популярность', 'название']

    def __str__(self):
        return self.название

    def get_absolute_url(self):
        return reverse('dish_detail', kwargs={'slug': self.slug})

    @property
    def текущая_цена(self):
        if self.акция and self.цена_со_скидкой:
            return self.цена_со_скидкой
        return self.цена

    @property
    def процент_скидки(self):
        if self.акция and self.цена_со_скидкой and self.цена > 0:
            return int((1 - self.цена_со_скидкой / self.цена) * 100)
        return 0

    @property
    def средний_рейтинг(self):
        отзывы = self.отзывы.all()
        if отзывы:
            return sum([o.рейтинг for o in отзывы]) / len(отзывы)
        return 0

    @property
    def количество_отзывов(self):
        return self.отзывы.count()


class Корзина(models.Model):
    пользователь = models.ForeignKey(User, on_delete=models.CASCADE, related_name='корзина')
    создано = models.DateTimeField(auto_now_add=True)
    обновлено = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'корзины'
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина {self.пользователь.username}"

    @property
    def общая_сумма(self):
        return sum(item.подитог for item in self.элементы.all())

    @property
    def количество_позиций(self):
        return self.элементы.count()


class ЭлементКорзины(models.Model):
    корзина = models.ForeignKey(Корзина, on_delete=models.CASCADE, related_name='элементы')
    блюдо = models.ForeignKey(Блюдо, on_delete=models.CASCADE)
    количество = models.PositiveIntegerField(default=1)
    добавлено = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'элементы_корзины'
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        unique_together = ['корзина', 'блюдо']

    def __str__(self):
        return f"{self.блюдо.название} x {self.количество}"

    @property
    def подитог(self):
        return self.количество * self.блюдо.текущая_цена


class Заказ(models.Model):
    СТАТУСЫ = [
        ('новый', '🆕 Новый'),
        ('подтвержден', '✅ Подтвержден'),
        ('готовится', '👨‍🍳 Готовится'),
        ('готов', '📦 Готов к выдаче'),
        ('выполнен', '🎉 Выполнен'),
        ('отменен', '❌ Отменен')
    ]

    пользователь = models.ForeignKey(User, on_delete=models.CASCADE, related_name='заказы')
    статус = models.CharField(max_length=20, choices=СТАТУСЫ, default='новый')
    общая_сумма = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    имя_клиента = models.CharField(max_length=100)
    телефон = models.CharField(max_length=20)
    адрес = models.TextField(blank=True)
    комментарий = models.TextField(blank=True)
    способ_оплаты = models.CharField(max_length=50, default='наличные', choices=[
        ('наличные', 'Наличные'),
        ('карта', 'Карта'),
        ('онлайн', 'Онлайн')
    ])
    создано = models.DateTimeField(auto_now_add=True)
    обновлено = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'заказы'
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-создано']

    def __str__(self):
        return f"Заказ #{self.id} - {self.имя_клиента}"

    def save(self, *args, **kwargs):
        if not self.общая_сумма:
            self.общая_сумма = self.рассчитать_сумму()
        super().save(*args, **kwargs)

    def рассчитать_сумму(self):
        return sum(item.подитог for item in self.элементы.all())


class ЭлементЗаказа(models.Model):
    заказ = models.ForeignKey(Заказ, on_delete=models.CASCADE, related_name='элементы')
    блюдо = models.ForeignKey(Блюдо, on_delete=models.CASCADE)
    количество = models.PositiveIntegerField(default=1)
    цена_на_момент = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'элементы_заказа'
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    def __str__(self):
        return f"{self.блюдо.название} x {self.количество}"

    @property
    def подитог(self):
        return self.количество * self.цена_на_момент


class Отзыв(models.Model):
    пользователь = models.ForeignKey(User, on_delete=models.CASCADE, related_name='отзывы')
    блюдо = models.ForeignKey(Блюдо, on_delete=models.CASCADE, related_name='отзывы')
    рейтинг = models.PositiveIntegerField(choices=[(i, '★' * i) for i in range(1, 6)])
    комментарий = models.TextField(blank=True)
    создано = models.DateTimeField(auto_now_add=True)
    обновлено = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'отзывы'
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-создано']
        unique_together = ['пользователь', 'блюдо']

    def __str__(self):
        return f"{self.пользователь.username} - {self.блюдо.название} ({self.рейтинг}/5)"


class Избранное(models.Model):
    пользователь = models.ForeignKey(User, on_delete=models.CASCADE, related_name='избранное')
    блюдо = models.ForeignKey(Блюдо, on_delete=models.CASCADE)
    добавлено = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'избранное'
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ['пользователь', 'блюдо']

    def __str__(self):
        return f"{self.пользователь.username} - {self.блюдо.название}"


class Профиль(models.Model):
    пользователь = models.OneToOneField(User, on_delete=models.CASCADE, related_name='профиль')
    телефон = models.CharField(max_length=20, blank=True)
    адрес = models.TextField(blank=True)
    дата_рождения = models.DateField(null=True, blank=True)
    предпочтения = models.JSONField(default=dict)
    аватар = models.CharField(max_length=500, blank=True)
    создано = models.DateTimeField(auto_now_add=True)
    обновлено = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'профили'
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.пользователь.username}"


class Промокод(models.Model):
    код = models.CharField(max_length=20, unique=True)
    описание = models.TextField(blank=True)
    скидка = models.IntegerField(verbose_name="Скидка в %")
    минимальная_сумма = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    активно = models.BooleanField(default=True)
    срок_действия = models.DateTimeField()
    использовано = models.IntegerField(default=0)
    создано = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'промокоды'
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return f"{self.код} (-{self.скидка}%)"

    @property
    def действителен(self):
        from django.utils import timezone
        return self.активно and self.срок_действия > timezone.now()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Профиль.objects.create(пользователь=instance)
        Корзина.objects.create(пользователь=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.профиль.save()