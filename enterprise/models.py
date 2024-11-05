from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class SingletonModel(models.Model):
    """Singleton Django Model

    Ensures there's always only one entry in the database, and can fix the
    table (by deleting extra entries) even if added via another mechanism.

    Also has a static load() method which always returns the object - from
    the database if possible, or a new empty (default) instance if the
    database is still empty. If your instance has sane defaults (recommended),
    you can use it immediately without worrying if it was saved to the
    database or not.

    Useful for things like system-wide user-editable settings.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Save object to the database. Removes all other entries if there
        are any.
        """
        self.__class__.objects.exclude(id=self.id).delete()
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """
        Load object from the database. Failing that, create a new empty
        (default) instance of the object and return it (without saving it
        to the database).
        """

        try:
            return cls.objects.get()
        except cls.DoesNotExist:
            return cls()


class Contacts(SingletonModel):
    name = models.CharField('название', max_length=150)
    phone = PhoneNumberField('телефон', db_index=True)
    email = models.EmailField('email', db_index=True)
    additional_phone = PhoneNumberField('доп. телефон', blank=True)
    additional_email = models.CharField('доп. email', max_length=150, blank=True)
    address = models.CharField('Адерс', max_length=250, blank=True, default='')
    fax = PhoneNumberField('факс', blank=True)
    insta = models.URLField('Инстаграмм', max_length=250, blank=True,)
    ok = models.URLField('Однокласники', max_length=250, blank=True,)
    fb = models.URLField('Facebook', max_length=250, blank=True,)
    vk = models.URLField('В Контакте', max_length=250, blank=True,)

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return self.name


class News(models.Model):

    title = models.CharField('Заголовок', max_length=200, db_index=True)
    picture = models.ImageField('Изображение', upload_to='pictures_news', null=True, blank=True)
    content = models.TextField('Содержание', blank=True)
    created_at = models.DateTimeField(
        'Дата создания', db_index=True, auto_now_add=True
    )

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
    
    def __str__(self):
        return self.title
    
    @property
    def get_image(self):
        return self.picture.url
