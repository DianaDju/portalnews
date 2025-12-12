from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import Group


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        # Сохраняем пользователя стандартным способом
        user = super().save_user(request, user, form, commit=commit)

        # Проверяем, что пользователь новый (has pk) и не в группе 'common'
        if commit and user.pk and not user.groups.filter(name='common').exists():
            try:
                # Получаем группу 'common' )
                common_group = Group.objects.get(name='common')
                user.groups.add(common_group)
                # Опционально: сохраняем изменения (Django обычно кэширует, но на всякий случай)
                user.save()

            except Group.DoesNotExist:
                pass

        return user