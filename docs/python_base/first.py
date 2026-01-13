# 基础数据类型
# 1. 整数
# a = 10
# print(type(a))

# 2. 浮点数
# b = 3.14
# print(type(b))

# 3. 字符串
c = "Hello, Python!"
# print(type(c))
# c = c.upper()
# c = c.replace("Python", "World")
# c = c.find('o',5,10)
# c = c.split(', '
# c = c.index('P')
# c = c[7:13:2] # 切片, 7开始到13，步长2
# print(c)

# 4. 布尔值
# d = True
# print(type(d))

# 5. 列表
e = [1, 2, 3, 4, 5 , 2.2]
# print(type(e))
# e.append(6)  # 添加元素
# e.remove(3)  # 删除元素
# e.insert(2, 2.5)  # 在索引2处插入元素
# e.sort()  # 排序
# e.reverse()  # 反转列表
# e = e[1:4]  # 切片
# e = e[::2]  # 步长为2的切片
# e = e[-1]  # 获取最后一个元素
# e = e.index(2)  # 获取元素2的索引
# e = e.count(2)  # 统计元素2的出现次数
# print(e)

# 6. 元组
f = (1, 2, 3, 4, 5)
# print(type(f))
# f = f[1:4]  # 切片
# f = f[::2]  # 步长为2的切片
# f = f[-1]  # 获取最后一个元素
# f = f.index(2)  # 获取元素2的索引
# f = f.count(2)  # 统计元素2的出现次数
# f = f + (6,)  # 添加元素，元组不可变
# f = f * 2  # 重复元组
# f = f[1:]  # 从索引1开始到结束
# f = f[:3]  # 从开始到索引3
# f = f[1:4:2]  # 从索引1到索引4，步长为2
# f = f[::-1]  # 反转元组
# print(f)

# 7. 字典
g = {'name': 'Alice', 'age': 25, 'city': 'New York'}
# print(type(g))
# g['age'] = 26  # 修改元素
# g['country'] = 'USA'  # 添加元素
# del g['city']  # 删除元素
# g_keys = g.keys()  # 获取所有键
# g_values = g.values()  # 获取所有值
# g_items = g.items()  # 获取所有键值对
# g_pop = g.pop('age')  # 删除并返回指定键的值
# g_clear = g.clear()  # 清空字典
# print(g)

# 8. 集合
h = {'xxx', 11, 0, 1, 2, 3, 4, 5} # 注意：集合中的元素必须是不可变类型
# print(type(h)) # <class 'set'>
# h.add(6)  # 添加元素
# h.remove(3)  # 删除元素，不存在会报错
# h.discard(101)  # 删除元素，不存在不会报错
# h.pop()  # 随机删除并返回一个元素 TIP: 集合是无序的，所以无法指定删除哪个元素
# h.clear()  # 清空集合
# h_union = h.union({4, 5, 6, 7})  # 并集
# h_intersection = h.intersection({4, 5, 6, 7})  # 交集
# h_difference = h.difference({4, 5, 6, 7})  # 差集(只在h中存在的元素)
# h_symmetric_difference = h.symmetric_difference({4, 5, 6, 7})  # 对称差集(在h或{4, 5, 6, 7}中，但不同时存在的元素)
# print(h_symmetric_difference)

# 9. None类型
i = None
# print(type(i))
# i = 10
# print(i)

# 10. 类型转换
j = "123"
# j = int(j)  # 字符串转整数
# j = float(j)  # 字符串转浮点数
# j = str(123)  # 整数转字符串
# j = list((1, 2, 3))  # 元组转列表
# j = tuple([1, 2, 3])  # 列表转元组
# j = set([1, 2, 2, 3])  # 列表转集合
# j = set((1,2, 2, 3, 5, 'xx', 'xx'))  # 元组转集合（还能去重）
# j = dict(name='Bob', age=30)  # 关键字参数转字典
# print(type(j))
# print(j)

# 11. 输入和输出
# name = input("请输入你的名字: ")
# print("你好，" + name + "！")
# print(c)

# 12. 注释
# 单行注释使用 #
#  多行注释使用三引号 ''' 或 """

# 13. 转义字符
k = "Hello,\nPython!\tWelcome to \'Python\' programming."
# print(k)
# print(r"Hello,\nPython!\tWelcome to \'Python\' programming.")  # 原始字符串，不转义
# print("Hello, \\ Python!")  # 输出 Hello, \ Python!
# print("She said, \"Hello!\"")  # 输出 She said, "Hello!"
# print('It\'s a beautiful day!')  # 输出 It's a beautiful day!
# print("C:\\Users\\Name")  # 输出 C:\Users\Name

# 14. 字符串格式化
name = "Alice"
age = 25
# 方法1: 使用 % 操作符
# info1 = "Name: %s, Age: %d" % (name, age)
# 方法2: 使用 str.format() 方法
# info2 = "Name: {}, Age: {}".format(name, age)
# 方法3: 使用 f-string (Python 3.6+)
# info3 = f"Name: {name}, Age: {age}"
# print(info2)

