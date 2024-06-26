import torch
import torch._dynamo as dynamo
from torch._inductor.decomposition import decompositions as inductor_decomp

from buddy.compiler.frontend import DynamoCompiler
from buddy.compiler.ops import tosa

def foo(x, y):
    return torch.matmul(x, y)

in1 = torch.randn(3, 2)
in2 = torch.randn(2, 4)

# Initialize the dynamo compiler.
dynamo_compiler = DynamoCompiler(
    primary_registry=tosa.ops_registry,
    aot_autograd_decomposition=inductor_decomp,
)

graphs = dynamo_compiler.importer(foo, in1, in2)
assert len(graphs) == 1
graph = graphs[0]
graph.lower_to_top_level_ir()
print(graph._imported_module)
# CHECK: module {
# CHECK-LABEL: func.func @forward
# CHECK: %{{.*}} = tosa.matmul
# CHECK: return %{{.*}}
# CHECK: }
# CHECK: }
