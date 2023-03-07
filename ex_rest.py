class Obj:
    def __init__(self, data):
        self.data = data
        self.id = None

    def __str__(self):
        return f"{self.__class__.__name__}({self.id})"


class ObjTab:
    cls = Obj

    def __init__(self):
        self.instances = {}

    def list(self):
        return self.instances.values()

    def get(self, id):
        return self.instances[id]

    def __getitem__(self, id):
        return self.get(id)

    def delete(self, id):
        del self.instances[id]

    def create(self, data):
        inst = self.cls(data)
        id = (max(self.instances.keys()) if self.instances else 0) + 1
        inst.id = id
        assert id not in self.instances
        self.instances[id] = inst
        return inst

    def replace(self, id, data):
        inst = self.cls(data)
        inst.id = id
        self.instances[id] = inst

    def update(self, id, data):
        inst = self.instances[id]
        inst.data.update(data)
        return inst

    def __str__(self):
        return f"{self.__class__.__name__}()"


class B(Obj):
    pass


class BTab(ObjTab):
    cls = B


class A(Obj):
    def __init__(self, data):
        self.data = data
        self.b = BTab()


class ATab(ObjTab):
    cls = A


def load_db():
    print("load_db")
    main = ATab()
    a1 = main.create("a1")
    a2 = main.create("a2")
    a1.b.create("a1b1")
    a1.b.create("a1b2")
    a2.b.create("a2b1")
    return main
