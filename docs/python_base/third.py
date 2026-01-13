from functools import reduce

### 函数
# - 函数定义与调用
# def greet(name):
#     return f"Hello, {name}!"
# print(greet("Alice"))

# - 参数类型：位置参数、默认参数、可变参数（`*args`、`**kwargs`）
# def introduce(name, age=18, *hobbies, **info):
#     introduction = f"Name: {name}, Age: {age}\n"
#     introduction += "Hobbies: " + ", ".join(hobbies) + "\n"
#     introduction += "Additional Info:\n"
#     for key, value in info.items():
#         introduction += f"  {key}: {value}\n"
#     return introduction
# print(introduce("Bob", 25, "Reading", "Traveling", city="New York", profession="Engineer"))

# - 参数传递方式：位置传参、关键字传参
# def add(a, b):
#     return a + b
# print(add(5, 10))            # 位置传参
# print(add(b=10, a=5))       # 关键字传参

# - 常用内置函数
# print(format(3.14159, '.2f'))  # 格式化数字
# print(len("Hello"))               # 内置函数字符串长度
# print(max(1, 5, 3, 9))          # 最大值
# print(min(1, 5, 3, 9))          # 最小值
# print(sum([1, 2, 3, 4, 5]))     # 求和
# print(sorted([5, 2, 9, 1]))    # 排序
# print(isinstance(123, int))   # 实例检查
# print(chr(97))               # ASCII 转换为字符
# print(ord('a'))              # 字符转换为 ASCII
# print(type(123))                # 类型检查
# print(range(5))               # 生成范围
# print(enumerate(['a', 'b', 'c'])) # 枚举
# print(zip([1, 2, 3], ['a', 'b', 'c'])) # 压缩
# print(map(str, [1, 2, 3]))          # 映射
# print(filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5])) # 过滤
# print(abs(-10))               # 绝对值
# print(round(3.14159, 2))     # 四舍五入
# print(chr(65))               # 字符转换
# print(ord('A'))              # ASCII转换
# print(bin(10))               # 二进制表示
# print(oct(10))               # 八进制表示
# print(hex(255))              # 十六进制表示
# print(eval("2 + 3 * 4"))    # 表达式求值
# print(id([1, 2, 3]))        # 对象标识符
# print(hash("hello"))         # 哈希值
# print(ascii("你好"))         # ASCII表示
# print(help(len))               # 帮助文档
# # 数据类型转换
# print(list("hello"))          # 转换为列表
# print(tuple((1, 2, 3)))      # 转换为元组
# print(set([1, 2, 2, 3]))      # 转换为集合
# print(dict([('a', 1), ('b', 2)]))        # 转换为字典
# print(str(123))              # 转换为字符串
# print(int("456"))            # 转换为整数
# print(float("3.14"))        # 转换为浮点数
# print(complex(2, 3))      # 转换为复数
# print(bytes("hello", 'utf-8'))  # 转换为字节
# print(bytearray(b"hello"))   # 转换为字节数组

# - 函数式编程概念（map, filter, reduce, lambda）
# numbers = [1, 2, 3, 4, 5]
# squared = list(map(lambda x: x ** 2, numbers))
# print(squared)  # 输出 [1, 4, 9, 16, 25]
# evens = list(filter(lambda x: x % 2 == 0, numbers))
# print(evens)    # 输出 [2, 4]
# product = reduce(lambda x, y: x * y, numbers)
# print(product)  # 输出 120

# - 装饰器（decorator）
# def decorator(func):
#     def wrapper(*args, **kwargs):
#         print("函数开始执行")
#         result = func(*args, **kwargs)
#         print("函数执行结束")
#         return result
#     return wrapper
# @decorator
# def say_hello(name):
#     print(f"Hello, {name}!")
# say_hello("Charlie")

# - 函数注解
# def add(a: int, b: int) -> int:
#     return a + b
# print(add(3, 5))

# - 返回值
# def divide(a, b):
#     if b == 0:
#         return None
#     return a / b
# print(divide(10, 2))  # 输出 5.0
# print(divide(10, 0))  # 输出 None

# - 匿名函数（lambda）
# add = lambda x, y: x + y
# print(add(4, 6))  # 输出 10

# - 闭包（closure）
# def outer_function(msg):
#     def inner_function():
#         print(msg)
#     return inner_function
# closure_func = outer_function("Hello from closure!")
# closure_func()  # 输出 "Hello from closure!"

# - 模块与包（import, from ... import）
# import math
# print(math.pi)  # 输出 3.141592653589793
# from math import pi
# print(pi)             # 输出 3.141592653589793

# - 异常处理（try, except, finally, raise）
# def safe_divide(a, b):
#     try:
#         return a / b
#     except ZeroDivisionError:
#         print("错误：除以零")
#         return None
#     finally:
#         print("执行结束")
# print(safe_divide(10, 2))  # 输出 5.0
# print(safe_divide(10, 0))  # 输出 错误：除以零
# def custom_error_example():
#     raise ValueError("这是一个自定义错误")
# custom_error_example()  # 会引发 ValueError

# - Lambda表达式
# square = lambda x: x ** 2
# print(square(5))  # 输出 25

# - 列表推导式
# squares = [x ** 2 for x in range(10)] # 遵循从左到右的顺序，先进行循环再进行计算
# print(squares)  # 输出 [0, 1, 4, 9, 16, 25, 36, 49, 64, 81] 

# - 作用域（局部变量、全局变量）
# global_var = "I am global"
# def scope_example():
#     local_var = "I am local"
#     print(local_var)      # 访问局部变量
#     print(global_var)    # 访问全局变量
# scope_example()
# print(global_var)        # 访问全局变量
# print(local_var)      # 会引发错误，无法访问局部变量

# - 递归函数
# def factorial(n):
#     if n == 0 or n == 1:
#         return 1
#     else:
#         return n * factorial(n - 1)
# print(factorial(5))  # 输出 120

# - 高阶函数（函数作为参数传递）
# def apply_function(func, value):
#     return func(value)
# def square(x):
#     return x * x
import builtins
print(dir(builtins))  # 输出所有内置函数和对象