import sys

_list = []
for i in range(10 ** 3):
    print(len(_list), sys.getsizeof(_list))
    _list.append(i)
