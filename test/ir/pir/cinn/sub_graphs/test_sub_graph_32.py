# Copyright (c) 2024 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# repo: PaddleClas
# model: ppcls^configs^ImageNet^ResNeSt^ResNeSt50
# api:paddle.tensor.manipulation.reshape||api:paddle.tensor.linalg.transpose||api:paddle.nn.functional.activation.softmax||api:paddle.tensor.manipulation.reshape
from base import *  # noqa: F403

from paddle.static import InputSpec


class LayerCase(paddle.nn.Layer):
    def __init__(self):
        super().__init__()

    def forward(
        self,
        # (shape: [22, 1024, 1, 1], dtype: paddle.float32, stop_gradient: True)
        var_0,
    ):
        var_1 = paddle.tensor.manipulation.reshape(
            x=var_0, shape=[22, 1, 2, 512]
        )
        var_2 = paddle.tensor.linalg.transpose(x=var_1, perm=[0, 2, 1, 3])
        var_3 = paddle.nn.functional.activation.softmax(var_2, axis=1)
        var_4 = paddle.tensor.manipulation.reshape(
            x=var_3, shape=[22, 1024, 1, 1]
        )
        return var_4


class TestLayer(TestBase):
    def init(self):
        self.input_specs = [
            InputSpec(
                shape=(-1, -1, -1, -1),
                dtype=paddle.float32,
                name=None,
                stop_gradient=True,
            )
        ]
        self.inputs = (
            paddle.rand(shape=[22, 1024, 1, 1], dtype=paddle.float32),
        )
        self.net = LayerCase
        self.with_train = False


if __name__ == '__main__':
    unittest.main()
