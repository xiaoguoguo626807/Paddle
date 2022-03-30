/* Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. */

#include <memory>
#include "paddle/fluid/framework/op_registry.h"

namespace paddle {
namespace operators {

class TrilIndicesOp : public framework::OperatorWithKernel {
 public:
  using framework::OperatorWithKernel::OperatorWithKernel;

  protected:
  framework::OpKernelType GetExpectedKernelType(
      const framework::ExecutionContext& ctx) const override {
    return framework::OpKernelType(framework::proto::VarType::INT64,
                                   ctx.device_context());
  }
};

class TrilIndicesOpMaker : public framework::OpProtoAndCheckerMaker {
 public:
  void Make() override {
    AddAttr<int>("Rows", "int number, the input of tril_indices op").SetDefault(0);;
    AddAttr<int>("Cols", "int number, the input of tril_indices op").SetDefault(0);;
    AddAttr<int>("Offset", "int number, the input of tril_indices op bounded by [1-rows,cols-1").SetDefault(0);
    AddAttr<int>("Dtype","data type ,the input of tril_indices op").SetDefault(int);
    AddOutput("Out","Tensor, the output tensor, with the shape (2,x),x bounded by [0,rows*cols])");
  
    AddComment(R"DOC(
TrilIndices Operator.

The tril_indices operator returns the indices of the lower triangular part of the matrix 
whose rows and cols is knowed in a 2-by-x tensor,where the first row contains row coordinates 
of all indices and the second row contains column coordinates. Indices are ordered based on 
rows and then columns. The lower triangular part of the matrix is defined as the elements on
 and below the diagonal.

The argument offset controls which diagonal to consider, default value is 0.A positive value
includes just as many diagonals above the main diagonal, and similarly a negative value
excludes just as many diagonals below the main diagonal

)DOC");
  }
};

}  // namespace operators
}  // namespace paddle

namespace ops = paddle::operators;

REGISTER_OPERATOR(tril_indices, ops::TrilIndicesOp, ops::TrilIndicesOpMaker,
                 paddle::framework::EmptyGradOpMaker<paddle::framework::OpDesc>,
                 paddle::framework::EmptyGradOpMaker<paddle::imperative::OpBase>);

