from petshop.mixins.base import AutoCrudMixinBase


class SearchMixin(AutoCrudMixinBase):



    def __init__(self):
        super().__init__(**kwargs)

        
        # init super
        self.schemas['search'] = build_model()


    
    
    # controller
    def search(self):     



        return self.method() + 20