from fastapi import Depends

from petshop.mixins.base import AutoCrudMixinBase


class ReadMixin(AutoCrudMixinBase):

    __config__ = None
    print ('meow')

    def __init__(self):
        super(ReadMixin).__init__(**kwargs)

        print ('INITTT')
        print ('READ')

        # build controller
        def func(self, id, db = Depends(get_db)):
            return db.query(self).filter(self.id == id).first()

        # attach controller
        self.controllers.read = func
        
        # build route
        self.router.add_api_route(
            "{id}",
            self.controllers.read,
            description="descriotion str",
            summary="summary str",
            tags=["tags"],
            operation_id="op_id",
            methods=["GET"],
            status_code=200,
            response_model=self,
        )
        print (self)