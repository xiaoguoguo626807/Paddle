# Copyright (c) 2025 PaddlePaddle Authors. All Rights Reserved.
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

cmake .. -DPY_VERSION=3.9 -DCMAKE_BUILD_TYPE=Release -DWITH_GPU=ON -DWITH_CUDNN_DSO=OFF -DWITH_SHARED_PHI=ON -DWITH_TENSORRT=ON -DWITH_ROCM=OFF -DWITH_CINN=OFF -DWITH_DISTRIBUTE=ON -DWITH_MKL=ON -DWITH_AVX=ON -DCUDA_ARCH_NAME=Manual -DNEW_RELEASE_PYPI=OFF -DNEW_RELEASE_ALL=OFF -DNEW_RELEASE_JIT=OFF -DWITH_PYTHON=ON -DCUDNN_ROOT=/usr/ -DWITH_TESTING=OFF -DWITH_COVERAGE=OFF -DWITH_INCREMENTAL_COVERAGE=OFF -DCMAKE_MODULE_PATH=/opt/rocm/hip/cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DWITH_INFERENCE_API_TEST=OFF -DINFERENCE_DEMO_INSTALL_DIR=/root/.cache/inference_demo -DCMAKE_INSTALL_PREFIX=/paddle/build -DWITH_PSCORE=OFF -DWITH_PSLIB=OFF -DWITH_GLOO=ON -DLITE_GIT_TAG=release/v2.10 -DWITH_XPU=OFF -DWITH_IPU=OFF -DXPU_SDK_ROOT= -DWITH_LITE=OFF -DWITH_XPU_BKCL=OFF -DWITH_ARM=OFF -DWITH_STRIP=ON -DON_INFER=ON -DWITH_HETERPS=OFF -DWITH_GPU_GRAPH=OFF -DCUDA_ARCH_BIN="70 75 80 86 90" -DWITH_RECORD_BUILDTIME=OFF -DWITH_UNITY_BUILD=OFF -DWITH_ONNXRUNTIME=OFF -DWITH_CUDNN_FRONTEND=OFF

我提供的2.6.1 应该是修复了几个问题：
1. sum mean运算错误，这种错误往往发生在一个CUDA Error之后。修复方式是，只要用我的环境编译就没问题，问题可能出现在早年2.6.2的发版打包环境上。不需要改代码。
2. slice的时候报expend错误，这个修改了代码：
3. spconv的一个问题。这个问题应该是修改了CMake的命令。用修改后的命令打包就行了。
4. https://github.com/LielinJiang/Paddle/tree/dataloader_wo_bq，用于dataloader内存占用优化，不然有些场景因为内存不够用PDC崩溃
    为了配合该工作,涉及的因为Tensor的api pin memory 多卡的问题，需要引入https://github.com/PaddlePaddle/Paddle/pull/69633
