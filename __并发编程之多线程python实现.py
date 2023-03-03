# encoding: utf-8
# @author: MrZhou
# @file: __并发编程之多线程python实现.py
# @time: 2023/2/27 20:17
# @desc:
import queue
import threading

# 第一种方式：面向过程

import time
import random
from threading import Thread
#
# def eat(name):
#     print("%s eating" % name)
#     time.sleep(random.randrange(1,5))
#     print('%s eat end' % name)
#
# if __name__ == '__main__':
#     t1=Thread(target=eat(),args=('jack',))
#     print('主')
#
# 面向对象
# class Mythread(Thread):
#     def __int__(self,name):
#         super().__int__()
#         self.name=name
#
#     def run(self):
#         print('%s eating' % self.name)
#         time.sleep(random.randrange(1, 5))
#         print('%s eat end' % self.name)
#
#
# if __name__ == '__main__':
#     t1 = Mythread('th1')
#     t2 = Mythread('th2')
#     t1.start()
#     t2.start()
#     print("主")
#
#
# 多线程与多进程的区别
# 1、开启速度 线程远远快过进程
# 2、pid:线程的pid与主进程一致而进程间的pid互不相同
# 3、地址空间：进程之间地址空间是隔离的，同一进程内开启的多个线程是共享该进程地址空间的
#
#
# Thread对象的其他属性或方法
# isAlive(): 返回线程是否活动的
# getName(): 返回线程名
# setName(): 设置线程名
#
# threading模块提供的一些方法
# threading.currentThread():返回当前的线程变量
# threading.enumerate():返回一个包含正在运行的线程list，正在运行指线程启动后，结束前，不包括启动前和终止后的线程
# threading.activeCount():返回正在运行的线程数量，与len(threading.enumerate())有相同的结果

# 守护进程
# 无论是进程还是线程都遵循：守护XX都会等待主XX运行完毕后被销毁
# 需要强调的是运行完毕并非终止运行
#
# 1、对主进程来说，运行完毕指的是主进程代码运行完毕
# 2、对主线程来说，运行完毕指的是主线程所在的进程内的所有非守护线程统统执行完毕，主进程才算运行完毕
#
# 即主进程执行完后会死掉(不管子进程)，而主线程运行完后会等所有非守护线程执行完毕

# from threading import Thread
# import time
# def sayhi(name):
#     time.sleep(2)
#     print('%s say hello' %name)
#
# if __name__ == '__main__':
#     t=Thread(target=sayhi,args=('egon',))
#     t.setDaemon(True) #必须在t.start()前设置，进程中是daemon=True
#     t.start()
#
#     print('主线程')
#     print(t.is_alive())

# GIL本质就是一把互斥锁，既然是互斥锁，所有互斥锁的本质都一样，都是将并发运行变成串行，以此来控制同一时间内共享数据只能被一个任务所修改，进而保证数据安全
#
# 首先确定一点：每次执行python程序，都会产生一个独立的进程。例如python test.py，python aaa.py，python bbb.py会产生n个不同的python进程，
# 在一个python的进程内，不仅有test.py的主线程或者由该主线程开启的其他线程，还有解释器开启的垃圾回收等解释器级别的线程，总之，所有线程都运行在这一个进程内，毫无疑问
#
# 1、所有数据共享，代码作为一种数据也是被所有线程共享的，test.py的所有代码以及cpython解释器的所有代码
# 例如test.py定义一个函数work，在进程内所有线程都能访问到work的代码，于是我们可以开启m个线程然后target都指向该代码，能访问到意味着就是可以执行。
# 2、所有线程的任务，都需要将任务的代码当做参数传给解释器的代码执行，即所有的线程要想运行自己的任务，首先需要解决的是能够访问到解释器的代码
#
# 3、如果多个线程的target=work 那么执行流程是多个线程先访问到解释器的代码，即拿到执行权限，然后将target的代码交给解释器的代码去执行

# 锁的目的是为了保护共享的数据，同一时间只能有一个线程来修改共享的数据
# 保护不同的数据就应该加不同的锁
#
# GIL是解释器级别的，后者保护用户自己开发的应用程序的数据，即Lock
# 1、100个线程去抢GIL锁，即抢执行权限
# 2、肯定有一个线程先抢到GIL，暂称为线程1，然后开始执行，一旦执行就会拿到lock.acquire()
# 3、极有可能线程1还没运行完毕就有另外一个线程2抢到GIL然后开始运行，但线程2发现互斥锁lock还没被线程1释放，于是阻塞，被迫交出执行权限即释放GIL
# 4、直到线程1重新抢到GIL，开始从上次暂停的位置继续执行，直到正常释放互斥锁lock,然后其他的线程再重复2 3 4的过程
#
# 有了GIL的存在，同一时刻同一进程只有一个线程被执行，也就是说进程可以利用多核但是开销大而python的多线程开销小却无法利用多核优势
#
# 多CPU意味着可以有多个核并行完成计算所以多核提升的是计算性能
# 每个CPU一旦遇上I/O阻塞，仍然需要等待所以多核对I/O操作没什么用处
#
# 我们有四个任务需要处理，处理方式肯定要玩出并发的效果解决方案有
# 1、开启四个进程
# 2、一个进程下开启四个线程
#
# 单核情况分析
# 如果四个任务是计算密集型没有多核并行计算，方案1徒增创建进程开销 方案2胜
# 如果四个任务是I/O密集型，方案1创建进程开销大，且进程切换速度远不如线程，方案2胜
#
# 多核情况下分析
# 如果四个任务是计算密集型，多核意味着并行计算，在python中一个进程中同一时刻只有一个线程执行，用不上多核 方案一胜
# 如果四个任务是I/O密集型，再多的核也解决不了I/O问题，方案2胜

# 结论：现在计算机基本上都是多核，python对于计算密集型的任务多线程的效率并不能带来多大性能上的提升
# 甚至不如串行没有大量切换，但是对于I/O密集型的任务效率还是有显著提升
#
# 多线程用于I/O密集型，如socket 爬虫 web
# 多进程用于计算密集型，如金融分析
#
# 死锁现象：
# 指两个或两个以上的进程或线程在执行过程中，因争夺资源而造成的一种互相等待的现象
# 若无外力作用，他们都将无法推进下去此
#
# 针对死锁现象的解决方案-递归锁
# 为了支持同一线程中多次请求同一资源，python提供了可重入锁RLock
#
# 线程queue
# 有三种不同的queue：
# 1、class queue.Queue(maxsize=0)队列 先进先出
# 2、class queue.lifoQueue(maxsize=0) 堆栈 后进先出
# 3、class queue.PriorityQueue(maxsize=0) 优先级队列：存储数据时可设置优先级的队列

# 基于多进程或多线程实现并发的套接字通信，
# 致命缺陷：服务的开启的进程数或线程数都会随着并发的客户端数目的增多而增多
# 这会对服务端主机带来巨大的压力，甚至于不堪重负而瘫痪，于是必须对服务端开启的进程数或线程数加以控制，让机器在一个自己
# 可以承受的范围内运行，这就是进程池或线程池的用途
#
# concurrent.futures 模块提供了高度封装的异步调用接口
# ThreadPoolExecutor:线程池，提供异步调用
# processPoolexecutor:进程池，提供异步调用
#
# 1、sunbmit(fn，*args,**kwargs)异步提交任务
# 2、map 取代for循环submit的操作
# 3、shutdown(wait=True)
# 相当于进程池的pool.close()+pool.join()操作
# 4、result(timeout=None)取得结果
# 5、add_done_callback(fn)回调函数

