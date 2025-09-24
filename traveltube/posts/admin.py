from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Comment, Follow, Group, Post, PostImage


class PostImagesAdmin(admin.StackedInline):
    model = PostImage


class PostAdmin(admin.ModelAdmin):
    inlines = [PostImagesAdmin]
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
        'image_show'
    )

    def image_show(self, obj):
        if obj.image:
            return mark_safe("<img src='{}' width='60' />"
                             .format(obj.image.url))
        return None

    image_show.__name__ = "Картинка"
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(PostImage)
class PostImagesAdmin(admin.ModelAdmin):
    list_display = (
        'image',
        'post',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Follow)
