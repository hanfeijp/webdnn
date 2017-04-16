# -*- coding:utf-8 -*-

"""
Kernel Builder for WebGPU

- kernel source generation
- schedule memory allocation
"""

import numpy as np

from graph_builder.backend.interface.kernel_builder import GraphDescriptorGenerator
from graph_builder.backend.webgpu.allocator import Allocator
from graph_builder.backend.webgpu.graph_descriptor_webgpu import GraphDescriptorWebGPU
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operator_builder import OperatorBuilder
from graph_builder.frontend.graph import Graph


class GraphDescriptorGeneratorWebGPU(GraphDescriptorGenerator):
    allocator: Allocator
    params_array: np.ndarray
    descriptor: GraphDescriptorWebGPU

    def __init__(self, graph: Graph):
        super().__init__(graph)
        self.params_array = None
        self.descriptor = None

    def generate(self) -> GraphDescriptorWebGPU:
        batch_size = 1
        params_layout, self.params_array = Allocator.allocate_params(self.graph)
        variable_layout = Allocator.allocate_variables(self.graph)
        operators = OperatorBuilder.build_from_graph(self.graph)

        kernels = []
        for operator in operators:
            kernels.extend(operator.convert_to_kernels(
                batch_size,
                params_layout,
                variable_layout,
                MetaBufferInjector()
            ))

        return GraphDescriptorWebGPU(
            kernels=kernels,
            params_layout=params_layout,
            variable_layout=variable_layout,
            inputs=self.graph.inputs,
            outputs=self.graph.outputs,
            batch_size=self.graph.batch_size
        )
