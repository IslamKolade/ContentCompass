from django.db import models
from authentication.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField
import random
from model_utils import FieldTracker



class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="categories_created")
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = RichTextField(blank=True, null=True)
    last_update_timestamp = models.DateTimeField(auto_now=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug or self.name != self._original_name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_name = self.name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('content:category', args=[self.id])

class Content(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_contents', db_index=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=350, unique=True, blank=True, db_index=True)
    description = RichTextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='category_contents')
    tags = TaggableManager(blank=True)
    ai_relevance_score = models.FloatField(default=0.0, help_text="Precomputed AI score (0.0-1.0)")
    last_update_timestamp = models.DateTimeField(auto_now=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)

    fields_to_check = ['title', 'description', 'category']
    tracker = FieldTracker(fields=fields_to_check)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.pk:
            self._original_tags = set(self.tags.names())
        else:
            self._original_tags = set()


    def save(self, *args, **kwargs):
        if not self.slug or self.tracker.has_changed('title'):
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while Content.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        if self.pk:
            tags_changed = set(self.tags.names()) != self._original_tags
            

        if any(self.tracker.has_changed(field) for field in self.fields_to_check) or tags_changed:
            self.ai_relevance_score = round(random.uniform(0.1, 0.99), 2)
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('content:content', args=[self.id])

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.title}'

