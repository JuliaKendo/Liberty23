from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField('Наименование', max_length=100, db_index=True)
    parent_category = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    identifier_1C = models.CharField(
        'Идентификатор 1С',
        max_length=50,
        blank=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
    

class Product(models.Model):

    name = models.CharField('Наименование', max_length=200, db_index=True)
    articul = models.CharField('Артикул', max_length=200, blank=True)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        related_name='category_products',
        db_index=True,
    )
    unit = models.CharField(
        'Единица измерения',
        max_length=20,
        default='штук',
        db_index=True,
        choices=(
            ('796', 'штук'),
            ('163', 'грамм'),
            ('166', 'кг'),
    ))
    stock = models.PositiveIntegerField(
        'Остаток', default=0, validators=[MinValueValidator(0)]
    ) 
    created_at = models.DateTimeField(
        'Дата создания', db_index=True, auto_now_add=True
    )
    product_type = models.CharField(
        'Тип',
        max_length=20,
        default='product',
        db_index=True,
        choices=(
            ('product', 'товар'),
            ('service', 'услуга'),
            ('gift_сertificate', 'подарочный сертификат')
    ))
    description = models.TextField('Описание', blank=True)
    identifier_1C = models.CharField(
        'Идентификатор 1С', max_length=50, blank=True, db_index=True
    )

    class Meta:
        verbose_name = 'Номенклатура'
        verbose_name_plural = 'Номенклатура'

    def __str__(self):
        return f'{self.articul} {self.name}'.strip()
    
    def natural_key(self):
        return (self.name, self.id, self.identifier_1C, )
    
    @property
    def get_images(self):
        product_images = ProductImage.objects.filter(product_id=self.id)
        return [product_image.image.url for product_image in product_images]
    
    @property
    def get_image(self):
        images = ProductImage.objects.filter(product_id=self.id)
        if images:
            image = images.first()
            return image.image.url


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Фото',
        related_name='product_images'
    )
    filename = models.CharField(
        'Имя файла', max_length=100, blank=True, db_index=True
    )
    image = models.ImageField('Фото номенклатуры', upload_to='product_images')

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
