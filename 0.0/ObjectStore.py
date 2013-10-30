
class ObjectStore:
    objects = dict()

    def addObject(self, object):
        self.objects[object.ID] = (object, True)