# Overview #
用于中小企业三层ssh信任服务器网络中进行文件传输和命令执行的命令行运维工具

三层ssh信任拓扑介绍：
  * 三层节点以同心圆方式分布
  * 最内层为一个节点，就是工具运行的位置，定义为root节点
  * 与root有直接信任关系的节点放在第二层，以此类推
因为，项目名来源于整个搭建和访问的过程，就像一张pizza，数据基础是面饼，节点是点缀上面的配料，任务是烤制，命令是食用。
### 现在，开始我们的奇妙烹饪过程吧。。。 ###

# Project Features #
  * Fabric模块负责ssh连接及操作
  * sqlobject模块负责与数据库连接
  * 主要代码实现节点间访问，及fabric调度

# Long Long Later #
  * 增加一层服务，负责目前命令行的操作
  * 命令行变为瘦客户端只负责调用

# Long Long Long Later #
  * 移动平台应用
  * 语音控制