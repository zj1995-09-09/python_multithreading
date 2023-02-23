# encoding: utf-8
# @author: MrZhou
# @file: __并发编程之多进程python实现.py
# @time: 2023/2/23 11:31
# @desc:
import os

# python多线程无法利用多核优势，想要充分使用多核CPU资源
# os.cpu_count()查看 大部分情况使用多进程 提供了multiprocessing
# multiprocessing 模块用来开启子进程，并在子进程中执行我们定制的任务比如函数
# 该模块与多线程模块threading的编程接口类似
# multiprocessing模块的功能众多：支持子进程、通信和共享数据、执行不同形式的同步
# 提供了process、queue、pipe、lock等组件
# 需要再次强调的一点是：与线程不同，进程没有任何共享状态，进程修改的数据，改动仅限于该进程内。
#
# process类的介绍
# #Process([group [, target [, name [, args [, kwargs]]]]])
# 由该类实例化得到的对象，表示一个子进程中的任务(尚未启动)
#
# 强调：
# 1、需要使用关键字的方式来指定参数
# 2、args指定的为传给target函数的位置参数，是一个元组形式，必须有逗号
#
# group参数未使用，值始终为None
# target表示调用对象，即子进程要执行的任务
# name为子进程的名称
# args表示调用对象的位置参数元组，args=(1,2,'jack',)  注意最后面的逗号不要忘记
# kwargs表示调用对象的字典,kwargs={'name':'jack','age':18}
#
#
# 方法介绍
# p.start()启动进程，并调用该子进程中的p.run
# p.run():进程启动时运行的方法，正是它去调用target指定的函数，我们自定义类的类中一定要实现该方法
# p.terminate():强制终止进程p，不会进行任何清理操作，如果p创建了子进程，该子进程就成了僵尸进程，
# 使用该方法需要特别小心这种情况。如果p还保存了一个锁那么也将不会被释放，进而导致死锁
# p.is_alive():如果p仍然运行，返回True
# p.join([timeout):主线程等待p终止(强调：是主线程处于等的状态，而p是处于运行的状态)。timeout是可选的超时时间
#
# 属性介绍
# p.daemon:默认是False，如果是true,代表p为后台运行的守护进程
# 当p的父进程终止时，p也随之停止，并且设定为True后，p不能创建自己的新进程，必须在p.start()之前设置
# p.name 进程的名称
# p.pid 进程的pid

process类的使用(两种方式开启进程)
创建并开启子进程的方式一(面向过程)
from multiprocessing import Process
import time


def task(name):
    print('%s is runing' % name)
    time.sleep(3)
    print('%s is done' % name)
if __name__ == '__main__':
    p = Process(target=task, args=('子进程1',))
    p.start() #仅仅是给操作系统发了一个信号，父子进程均为独立运行，相互不影响
    print('主进程')

创建并开启子进程的方式二（面向过程）：

from multiprocessing import Process
import time

class MyProcess(Process): #必须继承Process类
    def __int__(self,name):
        super().__int__()
        self.name=name

    def run(self): #进程函数用run表示
        print('%s is runing'% self.name)
        time.sleep(3)
        print('%s is done' % self.name)

if __name__ == '__main__':
    p=MyProcess('子进程1')
    p.start()


process对象的属性：name与pid

from multiprocessing import Process
import time
import random

def task(name):
    print('%s is piaoing' %name)
    time.sleep(random.randrange(1,5))
    print('%s is piao end' %name)

if __name__ == '__main__':
    p1=Process(target=task,args=('egon',),name='子进程1') #可以用关键参数来指定进程名，p1只是一个进程对象
    p1.start()
    print(p1.name,p1.pid)

process对象的方法之：terminate与is_alive
from multiprocessing import Process
import time
import random

def task(name):
    print('%s is piaoing' %name)
    time.sleep(random.randrange(1,5))
    print('%s is piao end' %name)

if __name__ == '__main__':
    p1=Process(target=task,args=('egon',))
    p1.start()

    p1.terminate()#关闭进程，不会立即关闭，所以is_alive立刻查看的结果可能还是存活
    print(p1.is_alive())#结果为True

    print('主')
    print(p1.is_alive())#结果为False

Process类对象的join方法:

如果主进程的任务在执行到某一阶段时，需要等待子进程执行完毕后才能继续执行，就需要
有一种机制能够让主进程检测子进程是否运行完毕，在子进程执行完毕后才继续执行，否则一直在原地阻塞，这就是join方法


from multiprocessing import Process
import time
import random
import os

def task():
    print('%s is piaoing' %os.getpid())
    time.sleep(random.randrange(1,3))
    print('%s is piao end' %os.getpid())

if __name__ == '__main__':
    p=Process(target=task)
    p.start()
    p.join() #等待p停止，才执行下一行代码
    print('主')


守护进程
如果有两个任务需要并发执行，那么开一个主进程和一个子进程分别去执行就ok了，如果子进程
的任务在主进程任务结束后就没有存在的必要了，那么该子进程应该在开启前就被设置成守护进程。
主进程代码运行结束，守护进程随即终止

其一：守护进程会在主进程代码执行结束后就终止
其二：守护进程内无法再开启子进程,否则抛出异常：AssertionError: daemonic processes are not allowed to have children。

互斥锁
顾名思义就是互相排斥，如果多个进程比喻多个人，互斥锁的工作原理就是多个人都要去争同一个资源
卫生间，一个人抢到卫生间后上一把锁，其他人都要等着，等到这个完成任务后释放锁，其他人才有可能有一个抢到......所以互斥锁的原理，
就是把并发改成穿行，降低了效率，但保证了数据安全不错乱。

from multiprocessing import Process,Lock #需要导入Lock模块
import time

def task(name,mutex):
    mutex.acquire()
    print('%s 1' % name)
    time.sleep(1)
    print('%s 1' % name)
    time.sleep(1)
    print('%s 1' % name)
    mutex.release()

if __name__ == '__main__':
    mutex=Lock()#实例化得到互斥锁
    for i in range(3):
        p = Process(target=task, args=('进程%s' % i, mutex))  # 传入子进程
        p.start()

互斥锁与join 模拟抢票软件
使用join可以将并发变成串行，互斥锁的原理也是将并发变成串行，那我们直接使用join就可以了，为何还要互斥锁？
实验发现使用join将并发改成穿行，确实能保证数据安全，但问题是连查票操作也变成只能一个一个人去查了，
很明显大家查票时应该是并发地去查询而无需考虑数据准确与否，此时join与互斥锁的区别就显而易见了，
join是将一个任务整体串行，而互斥锁的好处则是可以将一个任务中的某一段代码串行，比如只让task函数中的get任务串行

互斥锁小结
加锁可以保证多个进程修改同一块数据时，同一时间只有有一个任务可以进行修改，即串行的修改
没错速度是慢了 但牺牲了速度却保证了数据安全

虽然可以用文件共享数据实现进程间通信，但问题是
1、效率低 共享数据基于文件，而文件是硬盘上的数据
2、需要自己加锁处理

因此我们最好找寻一种解决方案能够兼顾：

1、效率高（多个进程共享一块内存的数据）
2、帮我们处理好锁问题。

这就是mutiprocessing模块为我们提供的基于消息的IPC通信机制：队列和管道。

队列和管道都是将数据存放于内存中，而队列又是基于(管道+锁)实现的，可以让我们从复杂的锁问题解脱出来，队列才是进程通信的最佳选择
我们应该避免使用共享数据，尽可能使用消息传递和队列，避免处理复杂的同步和锁问题
而且在进程数据增多时，往往可以获得更好的可扩展性



队列
进程之间彼此要互相隔离，要实现进程间通信IPC，multiprocessing模块支持两种形式
队列和管道 都是使用消息传递的

创建队列的类(底层就是以管道和锁定的方式实现)
Queue([maxsize]):创建共享的进程队列，Queue是多进程安全的队列，可以使用Queue实现
多进程之间的数据传递

maxsize是队列中允许最大项数，省略则无大小限制。
但需要明确：
    1、队列内存放的是消息而非大数据
    2、队列占用的是内存空间，因而maxsize即便是无大小限制也受限于内存大小

from multiprocessing import Process,Queue  # 需要导入Queue模块
import time
q=Queue(3)


生产者消费者模型
生产者指的是生产数据的任务，消费者指的是处理数据的任务，在并发编程中，如果生产者处理速度很快
而消费者处理数据很慢，那么生产者必须等待消费者处理完，才能继续生产数据

同样的道理，如果消费者的处理能力大于生产者，那么消费者必须等待生产者，为了解决这个问题于是引入了
生产者和消费者模式


生产者消费者模式是通过一个容器来解决生产者和消费者的强耦合问题。
生产者和消费者彼此之间不直接通讯，而通过阻塞队列来进行通讯，
所以生产者生产完数据之后不用等待消费者处理，直接扔给阻塞队列
消费者不找生产者要数据，而是直接从阻塞队列里取，阻塞队列就相当于一个缓冲区，平衡了生产者和消费者的处理能力。
这个阻塞队列就是用来给生产者和消费者解耦的

此时的问题是主进程永远不会结束，原因是 生产者p在生产完后就结束了，但是消费者c在取空了q之后，则一直处于死循环中且卡在q.get()
这一步。
我们的思路是发送结束信号，而有另外一种队列提供了这种机制

JoinableQueue([maxsize])
这就像是一个Queue对象，但队列允许项目的使用者通知生成者项目已经被成功处理。通知进程是使用共享的信号和条件变量来实现的。