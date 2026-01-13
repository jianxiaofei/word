# 1. 整数与浮点数
# a = 10
# b = 3.14
# print("整数a:", a, "类型:", type(a))
# print("浮点数b:", b, "类型:", type(b))

# 2. 字符串操作
# c = "Hello, Python!"
# c = c.upper()
# c = c.replace("Python", "World")
# c = c[c.find('Python'):c.find('Python')+6]  # 提取'Python'
# print(c)

# 3. 列表操作
# e = [1, 2, 3, 4, 5 , 2.2]
# e.append(50)
# e.remove(3)
# e.insert(2, 2.5)
# print(e[2:4])

# 4. 元组操作
# f = (1, 2, 3, 4, 5)
# f = f.count(2)  
# print(f)
# print(f[-1])  # 切片
# print(f.count(2))  

# 5. 字典操作
# g = {'name': 'Alice', 'age': 25, 'city': 'New York'}
# g['age'] = 26
# print(g)
# del g['city']
# print(g)
# print(g.keys())  # 使用get方法获取键对应的值
# print(g.values())

# 6. 集合操作
# h = {'xxx', 11, 0, 1, 2, 3, 4, 5}
# h.add(6)
# h.remove(3)
# h.discard(11)
# h_union = h.union({4, 5, 6, 7})  # 并集
# print(h_union)
# h_intersection = h.intersection({'xxx', 5, 6, 7})  # 交集
# print(h_intersection)
# h_difference = h.difference({4, 5, 6, 7})  # 差集 h - {4,5,6,7}
# print(h_difference)
# h_symmetric_difference = h.symmetric_difference({4, 5, 6, 7})  # 对称差集
# print(h_symmetric_difference)

# 7. 类型转换
# num_str = "123"
# num_int = int(num_str)  # 字符串转整数
# num_float = float(num_str)  # 字符串转浮点数
# str_from_int = str(123)  # 整数转字符串
# print(num_int, type(num_int))
# print(num_float, type(num_float))
# print(str_from_int, type(str_from_int))

''' 
1. 统计字符串中每个字符出现的次数（区分大小写）
输入一个字符串，输出每个字符出现的次数，结果用字典表示。
例如输入 "Hello, Python!"，输出：{'H': 1, 'e': 1, 'l': 2, ...}
'''
# input_str = input("请输入一个字符串: ")
# char_count = {}
# for char in input_str:
#     if char in char_count:
#         char_count[char] += 1
#     else:
#         char_count[char] = 1
# print(char_count)

'''
2. 列表去重并按从大到小排序
给定一个包含重复元素的列表，去重后按从大到小排序，输出结果为元组。
例如输入 [3, 1, 2, 3, 4, 2, 5]，输出 (5, 4, 3, 2, 1)
'''
# input_list = [3, 1, 2, 3, 4, 2, 5]
# unique_sorted_tuple = tuple(sorted(set(input_list), reverse=True))
# print(unique_sorted_tuple)

'''
3. 合并两个字典，若有相同的键则将值相加
例如：
d1 = {'a': 10, 'b': 20, 'c': 30}
d2 = {'b': 5, 'c': 15, 'd': 8}
合并后：{'a': 10, 'b': 25, 'c': 45, 'd': 8}
'''
# d1 = {'a': 10, 'b': 20, 'c': 30}
# d2 = {'b': 5, 'c': 15, 'd': 8}
# d_union = {}

# for k in d1:
#     if k in d2:
#         d_union[k] = d1[k] + d2[k]
#     else:
#         d_union[k] = d1[k]

# for k in d2:
#     if k not in d_union:
#         d_union[k] = d2[k]
    
# print(d_union)

'''
4. 找出两个集合的最大公共元素和最大只属于其中一个集合的元素
例如：
s1 = {1, 3, 5, 7, 9}
s2 = {2, 3, 5, 8, 9}
输出：

最大公共元素：9
最大只属于一个集合的元素：8
'''
# s1 = {1, 3, 5, 7, 9}
# s2 = {2, 3, 5, 8, 9}

# print(max(s1.intersection(s2)))
# print(max(s1.symmetric_difference(s2)))

'''
5. 用户输入一串数字（用逗号分隔），输出去重、排序后的列表和元组
例如输入："5,3,6,3,2,5,1"
输出：

列表：[1, 2, 3, 5, 6]
元组：(1, 2, 3, 5, 6)
'''
# user_input = input("请输入一串数字，逗号分割：")
# l = [int(x) for x in user_input.split(',')]
# l = set(l)
# l = list(l)
# l.sort()
# # print(l)
# print(tuple(l))