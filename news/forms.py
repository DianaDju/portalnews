from django import forms
from .models import Post  # Не обязательно, но для справки


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
        fields = ['title', 'text', 'author']  # Исключаем 'type', 'rating' — они устанавливаются в view
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }
