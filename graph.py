def read_array_from_file(file_name):
  nash_convs = []
  i = 0
  current_double = ""
  with open("kuhn_poker_external_sampling.txt",'r') as f:  
   while True:
       c = f.read(1)
       if c == " ":
         nash_convs.append(float(current_double))
         current_double = ""
         i += 1
       elif not c:
         print ("End of file")
         break
       else:
         current_double += c
  return nash_convs

from matplotlib import pyplot as plt
import numpy as np
file = "kuhn_poker_external_sampling.txt"
nash_convs_kuhn_external = read_array_from_file(file)
step = 1
max_value = len(nash_convs_kuhn_external)
x = np.arange(0, max_value, step)
y = np.array(nash_convs_kuhn_external)
plt.plot(x,y)
plt.xlabel("NashConv")
plt.ylabel("Iteration")
plt.title('NashConv evolution of External sampling for kuhn poker')
plt.show()
