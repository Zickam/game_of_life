import time

n = 10 ** 7

start = time.time()

c = 0
for i in range(n):
    c += 1

end = time.time()

print(end - start, "seconds passed")
print("iterations per second:", n / (end - start))
