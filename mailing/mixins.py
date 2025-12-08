from django.core.exceptions import PermissionDenied


class OwnerQuerysetMixin:
    """
    Для ListView/DetailView:
    - если у пользователя есть view_all_perm -> полный queryset
    - иначе фильтрация по owner_field (по умолчанию 'owner').
    """

    owner_field = "owner"
    view_all_perm: str | None = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if self.view_all_perm and user.has_perm(self.view_all_perm):
            return qs

        return qs.filter(**{self.owner_field: user})


class OwnerAccessMixin:
    """
    Для Update/Delete/View, где объект должен принадлежать текущему пользователю.
    Суперпользователь имеет полный доступ.
    """

    owner_field = "owner"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        owner = getattr(obj, self.owner_field, None)

        if owner is None:
            raise PermissionDenied("У объекта нет поля owner для проверки доступа.")

        if owner != request.user and not request.user.is_superuser:
            raise PermissionDenied("Недостаточно прав для доступа к этому объекту.")

        return super().dispatch(request, *args, **kwargs)
