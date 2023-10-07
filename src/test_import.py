from datetime import datetime
import random

now_timestamp = datetime.now().timestamp()
random.seed(now_timestamp)

excludes = set([6, 8]) # fill the two
all_numbers = set(range(1, 37)) - excludes
print(all_numbers)

selected_res = random.sample(all_numbers, k=3)
print(selected_res)