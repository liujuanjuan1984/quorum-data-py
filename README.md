# Python Data for Apps of QuoRum

quorum 常用数据结构的 python 封装：

1、feed：

基于 quorum 新共识，目前被 rum app、feed、port、circle 等几款产品采用的数据结构

参考：

- https://docs.rumsystem.net/docs/data-format-and-examples

请留意，这只是推荐结构，并不是唯一标准。quorum chain 是非常开放的，客户端完全可以按照自己的需求来构造上链数据的结构。

2、converter：

基于 quorum 新共识，从旧链 trx 或从 新链 trx 转换为待发布的数据。目前主要用作数据迁移：从旧共识链迁移到新共识链；在新共识链之间迁移。

3、trx_type：

判断 trx 的类型。该方法所返回的结果，与 rum-app，feed 等产品的处理保持一致。

### Install


```sh
pip install quorum_data_py
```

### Examples

```python

from quorum_data_py import feed

# create a new post data 
data = feed.new_post(content='hello guys')

# create a like post data
data = feed.like('a-post-id')

```

适用于 fullnode 也适用于 lightnode，比如：

```python

from quorum_data_py import feed
from quorum_fullnode_py import FullNode 

jwt = "xxx"
url = "xxx"

fullnode = FullNode(url,jwt)
data = feed.new_post(content='hello guys')
fullnode.api.post_content(data)

```

```python

from quorum_data_py import feed
from quorum_mininode_py import MiniNode 

seed = "xxx"

mininode = MiniNode(seed)
data = feed.new_post(content='hello guys')
mininode.api.post_content(data)

```

### Source

- quorum fullnode sdk for python: https://github.com/liujuanjuan1984/quorum-fullnode-py 
- quorum mininode sdk for python: https://github.com/liujuanjuan1984/quorum-mininode-py 
- and more ...  https://github.com/okdaodine/awesome-quorum

### License

This work is released under the `MIT` license. A copy of the license is provided in the [LICENSE](https://github.com/liujuanjuan1984/quorum_data_py/blob/master/LICENSE) file.
