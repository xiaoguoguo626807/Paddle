#   Copyright (c) 2018 PaddlePaddle Authors. All Rights Reserved.
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

import unittest

import numpy as np
from op_test import OpTest, convert_float_to_uint16, skip_check_grad_ci

import paddle
import paddle.fluid as fluid
import paddle.fluid.core as core
from paddle.fluid import Program, program_guard
from paddle.fluid.framework import convert_np_dtype_to_dtype_


class TestSumOp(OpTest):
    def setUp(self):
        self.python_api = paddle.sum
        self.op_type = "reduce_sum"
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((5, 6, 10)).astype("float64")}
        self.outputs = {'Out': self.inputs['X'].sum(axis=0)}
        self.attrs = {'dim': [0]}
        # reduce doesn't support float64 in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output(check_eager=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True, check_prim=True)


class TestSumOpFp32(OpTest):
    def setUp(self):
        self.python_api = paddle.sum
        self.op_type = "reduce_sum"
        self.prim_op_type = "prim"
        self.inputs = {
            'X': np.random.uniform(0, 0.1, (5, 6, 10)).astype("float16")
        }
        self.attrs = {'dim': [0, 1, 2]}
        self.outputs = {
            'Out': self.inputs['X'].sum(axis=tuple(self.attrs['dim']))
        }
        self.gradient = self.calc_gradient()
        # error occurred in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output(check_eager=True)

    def calc_gradient(self):
        x = self.inputs["X"]
        grad = np.ones(x.shape, dtype=x.dtype)
        return (grad,)

    def test_check_grad(self):
        self.check_grad(
            ['X'],
            'Out',
            user_defined_grads=self.gradient,
            check_eager=True,
            check_prim=True,
        )


class TestSumOp_ZeroDim(OpTest):
    def setUp(self):
        self.python_api = paddle.sum
        self.op_type = "reduce_sum"
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random([]).astype("float64")}
        self.outputs = {'Out': self.inputs['X'].sum(axis=None)}
        self.attrs = {'dim': [], 'reduce_all': True}
        # reduce doesn't support float64 in cinn.
        # 0-D tensor doesn't support in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output(check_eager=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True)


@unittest.skipIf(
    not core.is_compiled_with_cuda(), "core is not compiled with CUDA"
)
class TestSumOp_bf16(OpTest):
    def setUp(self):
        np.random.seed(100)
        self.python_api = paddle.sum
        self.op_type = "reduce_sum"
        self.prim_op_type = "prim"
        self.dtype = np.uint16
        self.x = np.random.uniform(0, 0.1, (2, 5, 10)).astype(np.float32)
        self.attrs = {'dim': [0, 1, 2]}
        self.out = self.x.sum(axis=tuple(self.attrs['dim']))
        self.gradient = self.calc_gradient()

        self.inputs = {'X': convert_float_to_uint16(self.x)}
        self.outputs = {'Out': convert_float_to_uint16(self.out)}
        self.gradient = self.calc_gradient()
        self.enable_cinn = False

    def test_check_output(self):
        place = core.CUDAPlace(0)
        self.check_output_with_place(place, check_eager=True)

    def test_check_grad(self):
        place = core.CUDAPlace(0)
        self.check_grad_with_place(
            place,
            ['X'],
            'Out',
            user_defined_grads=self.gradient,
            check_eager=True,
            check_prim=True,
        )

    def calc_gradient(self):
        x = self.x
        grad = np.ones(x.shape, dtype=x.dtype)
        return [grad]


class TestSumOp_fp16_withInt(OpTest):
    def setUp(self):
        self.python_api = paddle.sum
        self.op_type = "reduce_sum"
        self.prim_op_type = "prim"
        self.inputs = {
            # ref to https://en.wikipedia.org/wiki/Half-precision_floating-point_format
            # Precision limitations on integer values between 0 and 2048 can be exactly represented
            'X': np.random.randint(0, 30, (10, 10)).astype("float16")
        }
        self.attrs = {'dim': [0, 1]}
        self.outputs = {
            'Out': self.inputs['X'].sum(axis=tuple(self.attrs['dim']))
        }
        self.gradient = self.calc_gradient()
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output(check_eager=True)

    def calc_gradient(self):
        x = self.inputs["X"]
        grad = np.ones(x.shape, dtype=x.dtype)
        return (grad,)

    def test_check_grad(self):
        self.check_grad(
            ['X'],
            'Out',
            user_defined_grads=self.gradient,
            check_eager=True,
            check_prim=True,
        )


class TestSumOp5D(OpTest):
    def setUp(self):
        self.python_api = paddle.sum
        self.op_type = "reduce_sum"
        self.prim_op_type = "prim"
        self.inputs = {
            'X': np.random.random((1, 2, 5, 6, 10)).astype("float64")
        }
        self.attrs = {'dim': [0]}
        self.outputs = {'Out': self.inputs['X'].sum(axis=0)}
        # error occurred in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output(check_eager=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True, check_prim=True)


class TestSumOp6D(OpTest):
    def setUp(self):
        self.python_api = paddle.sum
        self.op_type = "reduce_sum"
        self.prim_op_type = "prim"
        self.inputs = {
            'X': np.random.random((1, 1, 2, 5, 6, 10)).astype("float64")
        }
        self.attrs = {'dim': [0]}
        self.outputs = {'Out': self.inputs['X'].sum(axis=0)}
        # error occurred in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output(check_eager=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True, check_prim=True)


class TestSumOp8D(OpTest):
    def setUp(self):
        self.python_api = paddle.sum
        self.op_type = "reduce_sum"
        self.inputs = {
            'X': np.random.random((1, 3, 1, 2, 1, 4, 3, 10)).astype("float64")
        }
        self.attrs = {'dim': (0, 3)}
        self.outputs = {'Out': self.inputs['X'].sum(axis=(0, 3))}

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True)


@skip_check_grad_ci(
    reason="reduce_max is discontinuous non-derivable function,"
    " its gradient check is not supported by unittest framework."
)
class TestMaxOp(OpTest):
    """Remove Max with subgradient from gradient check to confirm the success of CI."""

    def setUp(self):
        self.op_type = "reduce_max"
        self.python_api = paddle.max
        self.inputs = {'X': np.random.random((5, 6, 10)).astype("float64")}
        self.attrs = {'dim': [-1]}
        self.outputs = {
            'Out': self.inputs['X'].max(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestMaxOp_ZeroDim(OpTest):
    """Remove Max with subgradient from gradient check to confirm the success of CI."""

    def setUp(self):
        self.op_type = "reduce_max"
        self.python_api = paddle.max
        self.inputs = {'X': np.random.random([]).astype("float64")}
        self.attrs = {'dim': []}
        self.outputs = {
            'Out': self.inputs['X'].max(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


@skip_check_grad_ci(
    reason="reduce_min is discontinuous non-derivable function,"
    " its gradient check is not supported by unittest framework."
)
class TestMinOp(OpTest):
    """Remove Min with subgradient from gradient check to confirm the success of CI."""

    def setUp(self):
        self.op_type = "reduce_min"
        self.python_api = paddle.min
        self.inputs = {'X': np.random.random((5, 6, 10)).astype("float64")}
        self.attrs = {'dim': [2]}
        self.outputs = {
            'Out': self.inputs['X'].min(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestMinOp_ZeroDim(OpTest):
    """Remove Min with subgradient from gradient check to confirm the success of CI."""

    def setUp(self):
        self.op_type = "reduce_min"
        self.python_api = paddle.min
        self.inputs = {'X': np.random.random([]).astype("float64")}
        self.attrs = {'dim': []}
        self.outputs = {
            'Out': self.inputs['X'].min(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestMin6DOp(OpTest):
    """Remove Min with subgradient from gradient check to confirm the success of CI."""

    def setUp(self):
        self.op_type = "reduce_min"
        self.python_api = paddle.min
        self.inputs = {
            'X': np.random.random((2, 4, 3, 5, 6, 10)).astype("float64")
        }
        self.attrs = {'dim': [2, 4]}
        self.outputs = {
            'Out': self.inputs['X'].min(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestMin8DOp(OpTest):
    """Remove Min with subgradient from gradient check to confirm the success of CI."""

    def setUp(self):
        self.op_type = "reduce_min"
        self.python_api = paddle.min
        self.inputs = {
            'X': np.random.random((2, 4, 3, 5, 6, 3, 2, 4)).astype("float64")
        }
        self.attrs = {'dim': [2, 3, 4]}
        self.outputs = {
            'Out': self.inputs['X'].min(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


def raw_reduce_prod(x, dim=[0], keep_dim=False):
    return paddle.prod(x, dim, keep_dim)


class TestProdOp(OpTest):
    def setUp(self):
        self.op_type = "reduce_prod"
        self.python_api = raw_reduce_prod
        self.init_data_type()
        self.inputs = {'X': np.random.random((5, 6, 10)).astype(self.data_type)}
        self.outputs = {'Out': self.inputs['X'].prod(axis=0)}

    def init_data_type(self):
        self.data_type = (
            "float32" if core.is_compiled_with_rocm() else "float64"
        )

    def test_check_output(self):
        self.check_output(check_eager=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True)


class TestProdOp_ZeroDim(OpTest):
    def setUp(self):
        self.python_api = paddle.prod
        self.op_type = "reduce_prod"
        self.inputs = {'X': np.random.random([]).astype("float64")}
        self.outputs = {'Out': self.inputs['X'].prod()}
        self.attrs = {'dim': [], 'reduce_all': True}

    def test_check_output(self):
        self.check_output(check_eager=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True)


class TestProd6DOp(OpTest):
    def setUp(self):
        self.op_type = "reduce_prod"
        self.python_api = raw_reduce_prod
        self.init_data_type()
        self.inputs = {
            'X': np.random.random((5, 6, 2, 3, 4, 2)).astype(self.data_type)
        }
        self.attrs = {'dim': [2, 3, 4]}
        self.outputs = {
            'Out': self.inputs['X'].prod(axis=tuple(self.attrs['dim']))
        }

    def init_data_type(self):
        self.data_type = (
            "float32" if core.is_compiled_with_rocm() else "float64"
        )

    def test_check_output(self):
        self.check_output(check_eager=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True)


class TestProd8DOp(OpTest):
    def setUp(self):
        self.op_type = "reduce_prod"
        self.python_api = raw_reduce_prod
        self.init_data_type()
        self.inputs = {
            'X': np.random.random((2, 5, 3, 2, 2, 3, 4, 2)).astype(
                self.data_type
            )
        }
        self.attrs = {'dim': [2, 3, 4]}
        self.outputs = {
            'Out': self.inputs['X'].prod(axis=tuple(self.attrs['dim']))
        }

    def init_data_type(self):
        self.data_type = (
            "float32" if core.is_compiled_with_rocm() else "float64"
        )

    def test_check_output(self):
        self.check_output(check_eager=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_eager=True)


class TestAllOp(OpTest):
    def setUp(self):
        self.op_type = "reduce_all"
        self.python_api = paddle.all
        self.inputs = {'X': np.random.randint(0, 2, (5, 6, 10)).astype("bool")}
        self.outputs = {'Out': self.inputs['X'].all()}
        self.attrs = {'reduce_all': True}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAllOp_ZeroDim(OpTest):
    def setUp(self):
        self.python_api = paddle.all
        self.op_type = "reduce_all"
        self.inputs = {'X': np.random.randint(0, 2, []).astype("bool")}
        self.outputs = {'Out': self.inputs['X'].all()}
        self.attrs = {'dim': [], 'reduce_all': True}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAll8DOp(OpTest):
    def setUp(self):
        self.op_type = "reduce_all"
        self.python_api = paddle.all
        self.inputs = {
            'X': np.random.randint(0, 2, (2, 5, 3, 2, 2, 3, 4, 2)).astype(
                "bool"
            )
        }
        self.attrs = {'reduce_all': True, 'dim': (2, 3, 4)}
        self.outputs = {'Out': self.inputs['X'].all(axis=self.attrs['dim'])}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAllOpWithDim(OpTest):
    def setUp(self):
        self.op_type = "reduce_all"
        self.python_api = paddle.all
        self.inputs = {'X': np.random.randint(0, 2, (5, 6, 10)).astype("bool")}
        self.attrs = {'dim': (1,)}
        self.outputs = {'Out': self.inputs['X'].all(axis=self.attrs['dim'])}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAll8DOpWithDim(OpTest):
    def setUp(self):
        self.op_type = "reduce_all"
        self.python_api = paddle.all
        self.inputs = {
            'X': np.random.randint(0, 2, (2, 5, 3, 2, 2, 3, 4, 2)).astype(
                "bool"
            )
        }
        self.attrs = {'dim': (1, 3, 4)}
        self.outputs = {'Out': self.inputs['X'].all(axis=self.attrs['dim'])}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAllOpWithKeepDim(OpTest):
    def setUp(self):
        self.op_type = "reduce_all"
        self.python_api = paddle.all
        self.inputs = {'X': np.random.randint(0, 2, (5, 6, 10)).astype("bool")}
        self.attrs = {'dim': [1], 'keep_dim': True}
        self.outputs = {
            'Out': np.expand_dims(self.inputs['X'].all(axis=1), axis=1)
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAll8DOpWithKeepDim(OpTest):
    def setUp(self):
        self.op_type = "reduce_all"
        self.python_api = paddle.all
        self.inputs = {
            'X': np.random.randint(0, 2, (2, 5, 3, 2, 2, 3, 4, 2)).astype(
                "bool"
            )
        }
        self.attrs = {'dim': (5,), 'keep_dim': True}
        self.outputs = {
            'Out': np.expand_dims(
                self.inputs['X'].all(axis=self.attrs['dim']), axis=5
            )
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAllOpError(unittest.TestCase):
    def test_errors(self):
        with program_guard(Program(), Program()):
            # The input type of reduce_all_op must be Variable.
            input1 = 12
            self.assertRaises(TypeError, paddle.all, input1)
            # The input dtype of reduce_all_op must be bool.
            input2 = paddle.static.data(
                name='input2', shape=[-1, 12, 10], dtype="int32"
            )
            self.assertRaises(TypeError, paddle.all, input2)


class TestAnyOp(OpTest):
    def setUp(self):
        self.op_type = "reduce_any"
        self.python_api = paddle.any
        self.inputs = {'X': np.random.randint(0, 2, (5, 6, 10)).astype("bool")}
        self.outputs = {'Out': self.inputs['X'].any()}
        self.attrs = {'reduce_all': True}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAnyOp_ZeroDim(OpTest):
    def setUp(self):
        self.python_api = paddle.any
        self.op_type = "reduce_any"
        self.inputs = {'X': np.random.randint(0, 2, []).astype("bool")}
        self.outputs = {'Out': self.inputs['X'].any()}
        self.attrs = {'dim': [], 'reduce_all': True}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAny8DOp(OpTest):
    def setUp(self):
        self.op_type = "reduce_any"
        self.python_api = paddle.any
        self.inputs = {
            'X': np.random.randint(0, 2, (2, 5, 3, 2, 2, 3, 4, 2)).astype(
                "bool"
            )
        }
        self.attrs = {'reduce_all': True, 'dim': (3, 5, 4)}
        self.outputs = {'Out': self.inputs['X'].any(axis=self.attrs['dim'])}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAnyOpWithDim(OpTest):
    def setUp(self):
        self.op_type = "reduce_any"
        self.python_api = paddle.any
        self.inputs = {'X': np.random.randint(0, 2, (5, 6, 10)).astype("bool")}
        self.attrs = {'dim': [1]}
        self.outputs = {'Out': self.inputs['X'].any(axis=1)}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAny8DOpWithDim(OpTest):
    def setUp(self):
        self.op_type = "reduce_any"
        self.python_api = paddle.any
        self.inputs = {
            'X': np.random.randint(0, 2, (2, 5, 3, 2, 2, 3, 4, 2)).astype(
                "bool"
            )
        }
        self.attrs = {'dim': (3, 6)}
        self.outputs = {'Out': self.inputs['X'].any(axis=self.attrs['dim'])}

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAnyOpWithKeepDim(OpTest):
    def setUp(self):
        self.op_type = "reduce_any"
        self.python_api = paddle.any
        self.inputs = {'X': np.random.randint(0, 2, (5, 6, 10)).astype("bool")}
        self.attrs = {'dim': (1,), 'keep_dim': True}
        self.outputs = {
            'Out': np.expand_dims(
                self.inputs['X'].any(axis=self.attrs['dim']), axis=1
            )
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAny8DOpWithKeepDim(OpTest):
    def setUp(self):
        self.op_type = "reduce_any"
        self.python_api = paddle.any
        self.inputs = {
            'X': np.random.randint(0, 2, (2, 5, 3, 2, 2, 3, 4, 2)).astype(
                "bool"
            )
        }
        self.attrs = {'dim': (1,), 'keep_dim': True}
        self.outputs = {
            'Out': np.expand_dims(
                self.inputs['X'].any(axis=self.attrs['dim']), axis=1
            )
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestAnyOpError(unittest.TestCase):
    def test_errors(self):
        with program_guard(Program(), Program()):
            # The input type of reduce_any_op must be Variable.
            input1 = 12
            self.assertRaises(TypeError, paddle.any, input1)
            # The input dtype of reduce_any_op must be bool.
            input2 = paddle.static.data(
                name='input2', shape=[-1, 12, 10], dtype="int32"
            )
            self.assertRaises(TypeError, paddle.any, input2)


class Test1DReduce(OpTest):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random(120).astype("float64")}
        self.outputs = {'Out': self.inputs['X'].sum(axis=0)}
        # reduce doesn't support float64 in cinn.
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=True)


class Test2DReduce0(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.attrs = {'dim': [0]}
        self.inputs = {'X': np.random.random((20, 10)).astype("float64")}
        self.outputs = {'Out': self.inputs['X'].sum(axis=0)}
        # reduce doesn't support float64 in cinn.
        self.enable_cinn = False


class Test2DReduce1(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.attrs = {'dim': [1]}
        self.inputs = {'X': np.random.random((20, 10)).astype("float64")}
        self.outputs = {
            'Out': self.inputs['X'].sum(axis=tuple(self.attrs['dim']))
        }
        # reduce doesn't support float64 in cinn.
        self.enable_cinn = False


class Test3DReduce0(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.attrs = {'dim': [1]}
        self.inputs = {'X': np.random.random((5, 6, 7)).astype("float64")}
        self.outputs = {
            'Out': self.inputs['X'].sum(axis=tuple(self.attrs['dim']))
        }
        # reduce doesn't support float64 in cinn.
        self.enable_cinn = False


class Test3DReduce1(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.attrs = {'dim': [2]}
        self.inputs = {'X': np.random.random((5, 6, 7)).astype("float64")}
        self.outputs = {
            'Out': self.inputs['X'].sum(axis=tuple(self.attrs['dim']))
        }
        # reduce doesn't support float64 in cinn.
        self.enable_cinn = False


class Test3DReduce2(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.attrs = {'dim': [-2]}
        self.inputs = {'X': np.random.random((5, 6, 7)).astype("float64")}
        self.outputs = {
            'Out': self.inputs['X'].sum(axis=tuple(self.attrs['dim']))
        }
        # reduce doesn't support float64 in cinn.
        self.enable_cinn = False


class Test3DReduce3(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.attrs = {'dim': [1, 2]}
        self.inputs = {'X': np.random.random((5, 6, 7)).astype("float64")}
        self.outputs = {
            'Out': self.inputs['X'].sum(axis=tuple(self.attrs['dim']))
        }
        # reduce doesn't support float64 in cinn.
        self.enable_cinn = False


class Test8DReduce0(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.attrs = {'dim': (4, 2, 3)}
        self.inputs = {
            'X': np.random.random((2, 5, 3, 2, 2, 3, 4, 2)).astype("float64")
        }
        self.outputs = {
            'Out': self.inputs['X'].sum(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out')


class TestKeepDimReduce(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((5, 6, 10)).astype("float64")}
        self.attrs = {'dim': [1], 'keep_dim': True}
        self.outputs = {
            'Out': self.inputs['X'].sum(
                axis=tuple(self.attrs['dim']), keepdims=self.attrs['keep_dim']
            )
        }
        # reduce doesn't support float64 in cinn.
        self.enable_cinn = False


class TestKeepDim8DReduce(Test1DReduce):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.inputs = {
            'X': np.random.random((2, 5, 3, 2, 2, 3, 4, 2)).astype("float64")
        }
        self.attrs = {'dim': (3, 4, 5), 'keep_dim': True}
        self.outputs = {
            'Out': self.inputs['X'].sum(
                axis=tuple(self.attrs['dim']), keepdims=self.attrs['keep_dim']
            )
        }

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out')


@skip_check_grad_ci(
    reason="reduce_max is discontinuous non-derivable function,"
    " its gradient check is not supported by unittest framework."
)
class TestReduceMaxOpMultiAxises(OpTest):
    """Remove Max with subgradient from gradient check to confirm the success of CI."""

    def setUp(self):
        self.op_type = "reduce_max"
        self.python_api = paddle.max
        self.inputs = {'X': np.random.random((5, 6, 10)).astype("float64")}
        self.attrs = {'dim': [-2, -1]}
        self.outputs = {
            'Out': self.inputs['X'].max(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


@skip_check_grad_ci(
    reason="reduce_min is discontinuous non-derivable function,"
    " its gradient check is not supported by unittest framework."
)
class TestReduceMinOpMultiAxises(OpTest):
    """Remove Min with subgradient from gradient check to confirm the success of CI."""

    def setUp(self):
        self.op_type = "reduce_min"
        self.python_api = paddle.min
        self.inputs = {'X': np.random.random((5, 6, 10)).astype("float64")}
        self.attrs = {'dim': [1, 2]}
        self.outputs = {
            'Out': self.inputs['X'].min(axis=tuple(self.attrs['dim']))
        }

    def test_check_output(self):
        self.check_output(check_eager=True)


class TestKeepDimReduceSumMultiAxises(OpTest):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((5, 6, 10)).astype("float64")}
        self.attrs = {'dim': [-2, -1], 'keep_dim': True}
        self.outputs = {
            'Out': self.inputs['X'].sum(
                axis=tuple(self.attrs['dim']), keepdims=True
            )
        }

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        # rev_comp error
        self.check_grad(['X'], 'Out')


class TestReduceSumWithDimOne(OpTest):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((100, 1, 1)).astype("float64")}
        self.attrs = {'dim': [1, 2], 'keep_dim': True}
        self.outputs = {
            'Out': self.inputs['X'].sum(
                axis=tuple(self.attrs['dim']), keepdims=True
            )
        }
        # reduce doesn't support float64 in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=True)


class TestReduceSumWithNumelOne(OpTest):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((100, 1)).astype("float64")}
        self.attrs = {'dim': [1], 'keep_dim': False}
        self.outputs = {
            'Out': self.inputs['X'].sum(
                axis=tuple(self.attrs['dim']), keepdims=False
            )
        }
        # reduce doesn't support float64 in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=False)


class TestReduceAll(OpTest):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((100, 1, 1)).astype("float64")}
        self.attrs = {'reduce_all': True, 'keep_dim': False}
        self.outputs = {'Out': self.inputs['X'].sum()}
        # reduce doesn't support float64 in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=True)


class TestReduceAllFp32(OpTest):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((100, 1, 1)).astype("float32")}
        self.attrs = {'reduce_all': True, 'keep_dim': False}
        self.outputs = {'Out': self.inputs['X'].sum()}
        # reduce doesn't support float64 in cinn
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=True)


class Test1DReduceWithAxes1(OpTest):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random(100).astype("float64")}
        self.attrs = {'dim': [0], 'keep_dim': False}
        self.outputs = {'Out': self.inputs['X'].sum(axis=0)}
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output(check_prim=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=True)


class TestReduceWithDtype(OpTest):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = paddle.sum
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((6, 2, 10)).astype("float64")}
        self.outputs = {'Out': self.inputs['X'].sum().astype('float64')}
        self.attrs = {'reduce_all': True}
        self.attrs.update(
            {
                'in_dtype': int(convert_np_dtype_to_dtype_(np.float32)),
                'out_dtype': int(convert_np_dtype_to_dtype_(np.float64)),
            }
        )
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output(check_prim=True)

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=True)


def reduce_sum_wrapper(
    x, axis=None, dtype_rename=None, keepdim=False, name=None
):
    return paddle.sum(x, axis, "float64", keepdim, name)


class TestReduceWithDtype1(TestReduceWithDtype):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.python_api = reduce_sum_wrapper
        self.prim_op_type = "prim"
        self.inputs = {'X': np.random.random((6, 2, 10)).astype("float64")}
        self.outputs = {'Out': self.inputs['X'].sum(axis=1)}
        self.attrs = {'dim': [1]}
        self.attrs.update(
            {
                'in_dtype': int(convert_np_dtype_to_dtype_(np.float32)),
                'out_dtype': int(convert_np_dtype_to_dtype_(np.float64)),
            }
        )
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=True)


class TestReduceWithDtype2(TestReduceWithDtype):
    def setUp(self):
        self.op_type = "reduce_sum"
        self.prim_op_type = "prim"
        self.python_api = reduce_sum_wrapper
        self.inputs = {'X': np.random.random((6, 2, 10)).astype("float64")}
        self.outputs = {'Out': self.inputs['X'].sum(axis=1, keepdims=True)}
        self.attrs = {'dim': [1], 'keep_dim': True}
        self.attrs.update(
            {
                'in_dtype': int(convert_np_dtype_to_dtype_(np.float32)),
                'out_dtype': int(convert_np_dtype_to_dtype_(np.float64)),
            }
        )
        self.enable_cinn = False

    def test_check_output(self):
        self.check_output()

    def test_check_grad(self):
        self.check_grad(['X'], 'Out', check_prim=True)


class TestReduceSumOpError(unittest.TestCase):
    def test_errors(self):
        with program_guard(Program(), Program()):
            # The input type of reduce_sum_op must be Variable.
            x1 = fluid.create_lod_tensor(
                np.array([[-1]]), [[1]], fluid.CPUPlace()
            )
            self.assertRaises(TypeError, paddle.sum, x1)
            # The input dtype of reduce_sum_op  must be float32 or float64 or int32 or int64.
            x2 = paddle.static.data(name='x2', shape=[-1, 4], dtype="uint8")
            self.assertRaises(TypeError, paddle.sum, x2)


class API_TestSumOp(unittest.TestCase):
    def run_static(
        self, shape, x_dtype, attr_axis, attr_dtype=None, np_axis=None
    ):
        if np_axis is None:
            np_axis = attr_axis

        places = [fluid.CPUPlace()]
        if core.is_compiled_with_cuda():
            places.append(fluid.CUDAPlace(0))
        for place in places:
            with fluid.program_guard(fluid.Program(), fluid.Program()):
                data = fluid.data("data", shape=shape, dtype=x_dtype)
                result_sum = paddle.sum(
                    x=data, axis=attr_axis, dtype=attr_dtype
                )

                exe = fluid.Executor(place)
                input_data = np.random.rand(*shape).astype(x_dtype)
                (res,) = exe.run(
                    feed={"data": input_data}, fetch_list=[result_sum]
                )

            np.testing.assert_allclose(
                res,
                np.sum(input_data.astype(attr_dtype), axis=np_axis),
                rtol=1e-05,
            )

    def test_static(self):
        shape = [10, 10]
        axis = 1

        self.run_static(shape, "bool", axis, attr_dtype=None)
        self.run_static(shape, "bool", axis, attr_dtype="int32")
        self.run_static(shape, "bool", axis, attr_dtype="int64")
        self.run_static(shape, "bool", axis, attr_dtype="float16")

        self.run_static(shape, "int32", axis, attr_dtype=None)
        self.run_static(shape, "int32", axis, attr_dtype="int32")
        self.run_static(shape, "int32", axis, attr_dtype="int64")
        self.run_static(shape, "int32", axis, attr_dtype="float64")

        self.run_static(shape, "int64", axis, attr_dtype=None)
        self.run_static(shape, "int64", axis, attr_dtype="int64")
        self.run_static(shape, "int64", axis, attr_dtype="int32")

        self.run_static(shape, "float32", axis, attr_dtype=None)
        self.run_static(shape, "float32", axis, attr_dtype="float32")
        self.run_static(shape, "float32", axis, attr_dtype="float64")
        self.run_static(shape, "float32", axis, attr_dtype="int64")

        self.run_static(shape, "float64", axis, attr_dtype=None)
        self.run_static(shape, "float64", axis, attr_dtype="float32")
        self.run_static(shape, "float64", axis, attr_dtype="float64")

        shape = [5, 5, 5]
        self.run_static(shape, "int32", (0, 1), attr_dtype="int32")
        self.run_static(
            shape, "int32", (), attr_dtype="int32", np_axis=(0, 1, 2)
        )

    def test_dygraph(self):
        np_x = np.random.random([2, 3, 4]).astype('int32')
        with fluid.dygraph.guard():
            x = fluid.dygraph.to_variable(np_x)
            out0 = paddle.sum(x).numpy()
            out1 = paddle.sum(x, axis=0).numpy()
            out2 = paddle.sum(x, axis=(0, 1)).numpy()
            out3 = paddle.sum(x, axis=(0, 1, 2)).numpy()

        self.assertTrue((out0 == np.sum(np_x, axis=(0, 1, 2))).all())
        self.assertTrue((out1 == np.sum(np_x, axis=0)).all())
        self.assertTrue((out2 == np.sum(np_x, axis=(0, 1))).all())
        self.assertTrue((out3 == np.sum(np_x, axis=(0, 1, 2))).all())


class TestAllAPI(unittest.TestCase):
    def setUp(self):
        np.random.seed(123)
        paddle.enable_static()
        self.places = [fluid.CPUPlace()]
        if core.is_compiled_with_cuda():
            self.places.append(fluid.CUDAPlace(0))

    def check_static_result(self, place):
        with fluid.program_guard(fluid.Program(), fluid.Program()):
            input = fluid.data(name="input", shape=[4, 4], dtype="bool")
            result = paddle.all(x=input)
            input_np = np.random.randint(0, 2, [4, 4]).astype("bool")

            exe = fluid.Executor(place)
            fetches = exe.run(
                fluid.default_main_program(),
                feed={"input": input_np},
                fetch_list=[result],
            )
            np.testing.assert_allclose(fetches[0], np.all(input_np), rtol=1e-05)

    def test_static(self):
        for place in self.places:
            self.check_static_result(place=place)

    def test_dygraph(self):
        paddle.disable_static()
        for place in self.places:
            with fluid.dygraph.guard(place):
                np_x = np.random.randint(0, 2, (12, 10)).astype(np.bool_)
                x = paddle.assign(np_x)
                x = paddle.cast(x, 'bool')

                out1 = paddle.all(x)
                np_out1 = out1.numpy()
                expect_res1 = np.all(np_x)
                self.assertTrue((np_out1 == expect_res1).all())

                out2 = paddle.all(x, axis=0)
                np_out2 = out2.numpy()
                expect_res2 = np.all(np_x, axis=0)
                self.assertTrue((np_out2 == expect_res2).all())

                out3 = paddle.all(x, axis=-1)
                np_out3 = out3.numpy()
                expect_res3 = np.all(np_x, axis=-1)
                self.assertTrue((np_out3 == expect_res3).all())

                out4 = paddle.all(x, axis=1, keepdim=True)
                np_out4 = out4.numpy()
                expect_res4 = np.all(np_x, axis=1, keepdims=True)
                self.assertTrue((np_out4 == expect_res4).all())

        paddle.enable_static()


class TestAnyAPI(unittest.TestCase):
    def setUp(self):
        np.random.seed(123)
        paddle.enable_static()
        self.places = [fluid.CPUPlace()]
        if core.is_compiled_with_cuda():
            self.places.append(fluid.CUDAPlace(0))

    def check_static_result(self, place):
        with fluid.program_guard(fluid.Program(), fluid.Program()):
            input = fluid.data(name="input", shape=[4, 4], dtype="bool")
            result = paddle.any(x=input)
            input_np = np.random.randint(0, 2, [4, 4]).astype("bool")

            exe = fluid.Executor(place)
            fetches = exe.run(
                fluid.default_main_program(),
                feed={"input": input_np},
                fetch_list=[result],
            )
            np.testing.assert_allclose(fetches[0], np.any(input_np), rtol=1e-05)

    def test_static(self):
        for place in self.places:
            self.check_static_result(place=place)

    def test_dygraph(self):
        paddle.disable_static()
        for place in self.places:
            with fluid.dygraph.guard(place):
                np_x = np.random.randint(0, 2, (12, 10)).astype(np.bool_)
                x = paddle.assign(np_x)
                x = paddle.cast(x, 'bool')

                out1 = paddle.any(x)
                np_out1 = out1.numpy()
                expect_res1 = np.any(np_x)
                self.assertTrue((np_out1 == expect_res1).all())

                out2 = paddle.any(x, axis=0)
                np_out2 = out2.numpy()
                expect_res2 = np.any(np_x, axis=0)
                self.assertTrue((np_out2 == expect_res2).all())

                out3 = paddle.any(x, axis=-1)
                np_out3 = out3.numpy()
                expect_res3 = np.any(np_x, axis=-1)
                self.assertTrue((np_out3 == expect_res3).all())

                out4 = paddle.any(x, axis=1, keepdim=True)
                np_out4 = out4.numpy()
                expect_res4 = np.any(np_x, axis=1, keepdims=True)
                self.assertTrue((np_out4 == expect_res4).all())

        paddle.enable_static()


if __name__ == '__main__':
    paddle.enable_static()
    unittest.main()
