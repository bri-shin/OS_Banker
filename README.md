# OS Banker

*Operating System 2019 Fall*

*Author: Seung Heon Brian Shin*



### Program Background

The goal of this lab is to do resource allocation using both an optimistic resource manager and the banker’s algorithm of Dijkstra. The optimistic resource manager is simple: Satisfy a request if possible, if not make the task wait; when a release occurs, try to satisfy pending requests in a FIFO manner.



#### This program is composed of:

(Task Manager Componenets)

- Activity Class
- Task Class
- Task List Class



(Resource Allocation Methods)

- FIFO Class
- Banker Algorithm Class



### Program Specification

*Programming Language Used:* Python 3



### How to run this program

On the terminal, this program can be run by:

```bash
$ python3 run.py <input-file>
```

Example of input would be "input-01"