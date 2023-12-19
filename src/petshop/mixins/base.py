class Controllers(object):
    pass

class AutoCrudMixinBase(object):
    """
    expose a router on a db object table
    """

    def __init__(self, prefix, tags, dependencies, **kwargs):
        print ('base base base')
        super(AutoCrudMixinBase).__init__(**kwargs)

        # if no router exists, create one

        if not hasattr(self, 'router'):
            self.router = APIRouter(
                prefix=prefix,
                tags=tags,
                dependencies=dependencies,
            )

        self.controllers = Controllers()

        self.response_schema = None
        self.body_schema = None
        self.params = None





