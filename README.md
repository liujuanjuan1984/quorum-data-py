# Python Data for Apps of QuoRum

quorum 常用数据结构的 python 封装：

1、feed：

基于 quorum 新共识，目前被 rum app、feed、port、circle 等几款产品采用的数据结构

参考：

- https://docs.rumsystem.net/docs/data-format-and-examples

请留意，这只是推荐结构，并不是唯一标准。quorum chain 是非常开放的，客户端完全可以按照自己的需求来构造上链数据的结构。

2、converter：

基于 quorum 新共识，从旧链 trx 或从 新链 trx 转换为待发布的数据。目前主要用作数据迁移：从旧共识链迁移到新共识链；在新共识链之间迁移。

### Install


```sh
pip install quorum_data_py
```

### Examples

```python

from quorum_data_py import feed

data = feed.new_post(content='hello guys')
data = feed.like('a-post-id')

```

### pylint

```sh
isort ./quorum_data_py
black ./quorum_data_py
pylint ./quorum_data_py --output=pylint.log

```


### License

This work is released under the `MIT` license. A copy of the license is provided in the [LICENSE](https://github.com/liujuanjuan1984/quorum_data_py/blob/master/LICENSE) file.
