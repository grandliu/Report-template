@triton.jit
def _softcap_fwd_kernel(
    x_ptr,
    y_ptr,
    n_elements,
    softcap,
    BLOCK_SIZE: tl.constexpr,
):
    pid = tl.program_id(axis=0)
    grid_size = tl.num_programs(axis=0)
    num_blocks = tl.cdiv(n_elements, BLOCK_SIZE)
    for block_id in range(pid, num_blocks, grid_size):
        block_start = block_id * BLOCK_SIZE
        offsets = block_start + tl.arange(0, BLOCK_SIZE)
        mask = offsets < n_elements
        x = tl.load(x_ptr + offsets, mask=mask)
        # tanh(z) = 2*sigmoid(2z) - 1
        z = x.to(tl.float32) / softcap
        tanh_x = 2.0 * tl.sigmoid(2.0 * z) - 1.0
        y = softcap * tanh_x.to(x.dtype)
        tl.store(y_ptr + offsets, y, mask=mask)
