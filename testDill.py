import dill
import base64

class Queue():
    def __init__(self):
        self.data = []
    def add(self, item):
        self.data.append(item)
    def pop(self):
        return self.data.pop(0)

firstQueue = Queue()
firstQueue.add(1232312323)
firstQueue.add('adbcasdsd')
firstQueue.add(False)
nestedQueue = Queue()
nestedQueue.add('hello world')
firstQueue.add(nestedQueue)

class fibClass():
    def __init__(self,n):
        self.value = n
    def run(self):
        return self.fibonacci(self.value)
    def fibonacci(self,i):
        if i < 0:
            return 0
        if i==1:
            return 1
        else:
            return self.fibonacci(i - 1) + self.fibonacci(i - 2)

myClass = fibClass(10)

data = dill.dumps(firstQueue)
data = base64.b64encode(data)
#data = dill.dumps(myClass)
#data = base64.b64encode(data)
print(data)