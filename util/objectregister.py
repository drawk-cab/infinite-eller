#!/usr/bin/python3

import os, json

ROOT="/home/dave/projects/git/maze/storage"

class ObjectRegister:
    SINGLETON = None
    class __ObjectRegister:
        def __init__(self, classes=None):
            # print("Initing object register with classes %s" % classes)
            if classes is None:
                self.classes = {}
            else:
                self.classes = classes

        def getObject(self, obj):
            if isinstance(obj, dict) and '__class__' in obj:
                return self.classes[obj['__class__']](**obj)
            else:
                return obj

    def __init__(self, classes=None):
        if not ObjectRegister.SINGLETON:
            ObjectRegister.SINGLETON = ObjectRegister.__ObjectRegister(classes)
        elif classes is not None:
            # retain any classes already registered
            # print("Updating object register with classes %s" % classes)
            ObjectRegister.SINGLETON.classes.update(classes)


    def __getattr__(self, name):
        return getattr(ObjectRegister.SINGLETON, name)
