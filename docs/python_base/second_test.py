'''
题目1 — 统计并分类数字序列:

描述：编写函数 classify_numbers(nums)，接受整数列表 nums，返回字典包含以下统计信息：总数 count、正数个数 pos、负数个数 neg、零个数 zero、平均值 avg（float，四舍五入到 2 位小数）、正数列表 positives（按原顺序）、负数列表 negatives（按绝对值从小到大排序）。
输入输出示例：classify_numbers([0,3,-1,2,-4]) -> {'count':5,'pos':2,'neg':2,'zero':1,'avg':0.0,'positives':[3,2],'negatives':[-1,-4]}
约束：若 nums 为空，抛出 ValueError("empty list")。
难度：中等。
提示：使用 sum/len，列表推导，内置 sorted 的 key 参数以及异常处理。
练习点：列表遍历、条件统计、异常、排序与格式化数字
'''
# def classify_numbers(nums):
#     if not nums:
#         raise ValueError("empty list")
    
#     count = len(nums)
#     pos = sum(1 for x in nums if x > 0)
#     neg = sum(1 for x in nums if x < 0)
#     zero = sum(1 for x in nums if x == 0)
#     avg = round(sum(nums) / count, 2) if count > 0 else 0.0
#     positives = [x for x in nums if x > 0]
#     negatives = sorted([x for x in nums if x < 0], key=abs)

#     return {
#         'count': count,
#         'pos': pos,
#         'neg': neg,
#         'zero': zero,
#         'avg': avg,
#         'positives': positives,
#         'negatives': negatives
#     }


# print(classify_numbers([0, 3, -1, 2, -4]))

'''
题目2 — 自定义计时器与日志（流程控制 + 函数）:

描述：实现 timed_retry(func, retries=3, delay=1)，该函数接收一个无参可调用对象 func，尝试执行最多 retries 次；每次异常时等待 delay 秒后重试；
     若成功返回 ("ok", result, attempts, total_time)，
     失败（所有重试后仍异常）返回 ("error", last_exception, attempts, total_time)。
     attempts 为实际尝试次数，total_time 为总耗时（秒，保留 3 位小数）。不要在函数内直接 print，仅返回值以便测试。
示例：对某个偶发抛异常的短函数可看到重试次数变化。
约束：用 time.perf_counter() 计时；delay 可以为 0（立即重试）。
难度：中等偏上。
提示：使用 try/except、time.sleep、循环与累加时长。
练习点：异常处理、循环控制、时间测量、返回复杂结构便于断言。
'''
# import time
# def timed_retry(func, retries=3, delay=1):
#     attempts = 0
#     total_time = 0.0
#     last_exception = None

#     start_time = time.perf_counter()

#     for attempt in range(1, retries + 1):
#         attempts += 1
#         try:
#             result = func()
#             total_time = time.perf_counter() - start_time
#             return ("ok", result, attempts, round(total_time, 3))
#         except Exception as e:
#             last_exception = e
#             if attempt < retries:
#                 time.sleep(delay)

#     total_time = time.perf_counter() - start_time
#     return ("error", last_exception, attempts, round(total_time, 3))

# print(timed_retry(lambda: 1/0, retries=2, delay=0.5))