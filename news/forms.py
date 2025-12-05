
from .models import Post  # Не обязательно, но для справки
from django import forms
from .models import Category, CategorySubscription

class SearchForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        required=False,
        label='Заголовок новости',
        widget=forms.TextInput(attrs={'placeholder': 'Введите заголовок...'})
    )
    author = forms.CharField(
        max_length=100,
        required=False,
        label='Автор (имя автора)',
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя автора...'})
    )
    date = forms.DateField(
        required=False,
        label='Дата (дд.мм.гггг)',
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Выберите дату'})
    )


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text' ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }


class SubscribeCategoryForm(forms.ModelForm):
    """Форма для подписки на категорию."""
    class Meta:
        model = CategorySubscription
        fields = []  # Нет полей: данные из view (user, category)

    def __init__(self, *args, user=None, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.category = category
        self.instance = CategorySubscription(user=self.user, category=self.category)

class UnsubscribeCategoryForm(forms.ModelForm):
    """Форма для отписки от категории (удаление)."""
    class Meta:
        model = CategorySubscription
        fields = []  # Нет полей

    def __init__(self, *args, user=None, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.category = category