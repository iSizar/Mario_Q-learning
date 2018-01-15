import matplotlib.pyplot as plt

f = open("D:\PMP\LAB2\\filename.txt","r")
m = f.read()
xs = []
ys = []
m = m.split()
for i in range(0,len(m),2):
    xs.append(int(m[i]))
    ys.append(float(m[i+1]))
plt.plot(xs, ys, 'k')
plt.ylabel('some numbers')
plt.show()