# Python Data for Apps of QuoRum

适用于 rum app，feed，port，circle 等几款产品的推荐数据结构

参考：
- https://docs.rumsystem.net/docs/data-format-and-examples

### Install


```sh
pip install quorum_data_py
```

### Examples

```python

from quorum_data_py import FeedData as feed

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
