from django.contrib import admin
from .models import Post, PostCategory, Author, Category, Comment, CategorySubscription
from django.contrib import messages

class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1
    fields = ('category',)

class PostAdmin(admin.ModelAdmin):
    fields = ('author', 'post_type', 'title', 'text', 'rating', 'is_published')
    inlines = [PostCategoryInline]
    readonly_fields = ('time_created',)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Проверка категорий
        if not form.instance.categories.exists():
            messages.warning(
                request,
                "Пост должен иметь хотя бы одну категорию. Добавьте категории через 'Категории поста'."
            )

admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(CategorySubscription)




