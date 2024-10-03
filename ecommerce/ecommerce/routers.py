class MultiServiceRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'orders':
            return 'orders_db'
        elif model._meta.app_label == 'products':
            return 'products_db'
        elif model._meta.app_label == 'users':
            return 'users_db'  # or 'users_db' if that's what you intended
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'orders':
            return 'orders_db'
        elif model._meta.app_label == 'products':
            return 'products_db'
        elif model._meta.app_label == 'users':
            return 'users_db'  # or 'users_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label in ['orders', 'products', 'users'] and \
       obj2._meta.app_label in ['orders', 'products', 'users', 'auth']:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'orders':
            return db == 'orders_db'
        elif app_label == 'products':
            return db == 'products_db'
        elif app_label == 'users':
            return db == 'users_db'  # or 'users_db'
        return None
