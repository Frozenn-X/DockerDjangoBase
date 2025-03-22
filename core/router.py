class DatabaseRouter:
    """
    Routeur pour gérer les modèles entre MySQL et MongoDB.
    Les modèles Document de mongoengine sont automatiquement gérés par MongoDB.
    """
    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True 