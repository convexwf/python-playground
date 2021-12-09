# TIM 聊天记录导出

db_path: TIM 存储目录，一般默认为 `/storage/emulated/0/Android/data/com.tencent.tim/Tencent/Tim/`
qq_self: 个人 qq 号
qq_target: 目标 qq 号，好友或者群聊

解密文件存储在
`{db_path}/files/kc`
聊天记录数据库存储在
`{db_path}/databases/{qq_self}.db` 和 `{db_path}/databases/slowtable_{qq_self}.db`
聊天记录图片存储在
`/storage/emulated/0/Android/data/com.tencent.tim/Tencent/Tim/chatpic/chatimg`

## 目录结构

```txt
.
├── chatimg
├── databases
│   ├── 735165920.db
│   └── slowtable_735165920.db
├── files
│   └── kc
├── emoji
│   ├── face_config.json
│   ├── new
│   └── old
└── 材料清单.txt
```

## 消息类型

其中 cnt 为一段时间内的累计出现次数

msgtype    cnt     意义

-1000    339279  文字消息
-1051    0       文字消息
-2000    42514   图片
-2007    1670    自定义表情（？）
-1035    1522    混合类型数据
-1049    690     文字消息（回复）
-2009    599     语音或视频通话
-5040    379     疑似消息撤回
-2011    269     分享消息
-1001    154
-2005    101     分享文件
-5008    19      分享卡片
-5012    3       戳一戳
-5018    0       戳一戳
-2022    22      短视频

## sql 语句

```sql
-- 创建表
CREATE TABLE friend_{} (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    msgdata TEXT,
    msgtype INTEGER,
    msgseq INTEGER,
    msgId INTEGER,
    msgUid INTEGER,
    time INTEGER,
    senderId INTEGER,
    senderName TEXT,
    shmsgseq INTEGER,
    uniseq INTEGER,
    extStr TEXT,
    UNIQUE(time,senderId,msgdata,shmsgseq,msgseq) ON CONFLICT IGNORE
)

-- 创建索引
CREATE INDEX friend_{}_idx ON friend_{}(time, _id)

-- 查找好友 qq 号以及昵称
SELECT uin, name FROM Friends

-- 查找群友 qq 号以及昵称
SELECT troopuin, memberuin, friendnick FROM TroopMemberInfo

-- 查询记录
select msgData, msgtype, senderuin, time, msgseq, msgId, msgUid, shmsgseq, uniseq, extStr
from mr_{}_{}_New  order by time
```

## ON CONFLICT 子句

ON CONFLICT子句不是标准的SQL语言。`ON CONFLICT ROLLBACK | ABORT | FAIL | IGNORE | REPLACE`

- ROLLBACK
    当发生约束冲突，立即ROLLBACK，即结束当前事务处理，命令中止并返回SQLITE_CONSTRAINT代码。若当前无活动事务(除了每一条命令创建的默认事务以外)，则该算法与ABORT相同。
- ABORT
    当发生约束冲突，命令收回已经引起的改变并中止返回SQLITE_CONSTRAINT。但由于不执行ROLLBACK，所以前面的命令产生的改变将予以保留。缺省采用这一行为。
- FAIL
    当发生约束冲突，命令中止返回SQLITE_CONSTRAINT。但遇到冲突之前的所有改变将被保留。例如，若一条UPDATE语句在100行遇到冲突100th，前99行的改变将被保留，而对100行或以后的改变将不会发生。
- IGNORE
    当发生约束冲突，发生冲突的行将不会被插入或改变。但命令将照常执行。在冲突行之前或之后的行将被正常的插入和改变，且不返回错误信息。
- REPLACE
    当发生UNIQUE约束冲突，先存在的，导致冲突的行在更改或插入发生冲突的行之前被删除。这样，更改和插入总是被执行。命令照常执行且不返回错误信息。当发生NOT NULL约束冲突，导致冲突的NULL值会被字段缺省值取代。若字段无缺省值，执行ABORT算法。

当冲突应对策略为满足约束而删除行时，它不会调用删除触发器。但在新版中这一特性可能被改变。

## changelog

### 2021-12-10

1. 混合数据处理
2. 增加对一些其他消息类型的支持
3. 使用 ON CONFLICT 子句实现更新插入

TODO

1. 转发和分享消息
2. 5040 撤回消息类型的处理
3. 自定义表情
4. requirements.txt

### 2021-12-09

1. 实现基本的记录导出
2. 导出文本结果存储在 sqlite
3. 导出图片转储为 png 形式

TODO

1. ~~插入已有数据应该是更新而非忽略~~
2. 增加对其他信息类型的支持
3. ~~图像类数据描述的进一步优化~~
4. ~~表情包 和 混合数据~~
5. qqBot
6. 出现了 seq 为 0 的情况？

需要了解

1. 了解 python bytes以及string 的关系
2. proto 是干什么的？图片和 base64 的关系
