from app.db.exceptions import DbObjectDoesNotExist


class BaseDbRepo:

    async def check_object_exists(self, obj):
        if not obj:
            raise DbObjectDoesNotExist
